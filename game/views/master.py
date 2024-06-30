from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, ListView, UpdateView
from viewflow.fsm import TransitionNotAllowed

from character.models.character import Character

from ..constants.combat import CombatChoices
from ..constants.events import RollType
from ..flows import GameFlow
from ..forms import AbilityCheckRequestForm, QuestCreateForm, CombatCreateForm
from ..models.combat import Combat, Fighter
from ..models.events import Event, Quest
from ..models.game import Player
from ..schemas import GameEventType, PlayerType
from ..tasks import send_mail
from ..utils.cache import game_key
from ..utils.channels import send_to_channel
from ..utils.emails import get_players_emails
from ..views.mixins import EventContextMixin, GameContextMixin, GameStatusControlMixin


class CharacterInviteView(UserPassesTestMixin, ListView, GameContextMixin):
    model = Character
    paginate_by = 10
    ordering = ["-xp"]
    template_name = "game/character_invite.html"

    def test_func(self):
        return self.is_user_master()

    def get_queryset(self):
        return super().get_queryset().filter(player__game=None)


class CharacterInviteConfirmView(UserPassesTestMixin, UpdateView, GameContextMixin):
    model = Character
    fields = []  # type: list[str]
    template_name = "game/character_invite_confirm.html"

    def test_func(self):
        return self.is_user_master()

    def post(self, request, *args, **kwargs):
        character = self.get_object()
        Player.objects.create(character=character, game=self.game)
        event = Event.objects.create(game=self.game)
        event.date = timezone.now()
        event.message = f"{character} was added to the game."
        event.save()
        send_mail.delay(
            subject=f"The Master invited you to join [{self.game}].",
            message=f"{character}, the Master invited you to join [{self.game}].",
            from_email=self.game.master.user.email,
            recipient_list=[character.user.email],
        )
        return HttpResponseRedirect(reverse("game", args=(self.game.id,)))


class GameStartView(UserPassesTestMixin, GameStatusControlMixin):
    fields = []  # type: list[str]
    template_name = "game/game_start.html"

    def test_func(self):
        return self.is_user_master()

    def post(self, request, *args, **kwargs):
        game = self.get_object()
        flow = GameFlow(game)
        try:
            flow.start()
            cache.set(game_key(game.id), game)
            event = Event.objects.create(game=game)
            event.date = timezone.now()
            event.message = "the game started."
            event.save()

            send_to_channel(
                game_id=game.id,
                game_event={
                    "type": GameEventType.GAME_START,
                    "player_type": PlayerType.MASTER,
                    "date": event.date.isoformat(),
                    "message": event.message,
                },
            )

        except TransitionNotAllowed:
            return HttpResponseRedirect(reverse("game-start-error", args=(game.id,)))
        return HttpResponseRedirect(game.get_absolute_url())


class GameStartErrorView(UserPassesTestMixin, GameStatusControlMixin):
    fields = []  # type: list[str]
    template_name = "game/game_start_error.html"

    def test_func(self):
        return self.is_user_master()


class QuestCreateView(UserPassesTestMixin, FormView, EventContextMixin):
    model = Quest
    fields = ["description"]
    template_name = "game/quest_create.html"
    form_class = QuestCreateForm

    def test_func(self):
        return self.is_user_master()

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game.id,))

    def form_valid(self, form):
        quest = Quest()
        quest.game = self.game
        quest.message = "the Master updated the campaign."
        quest.content = form.cleaned_data["content"]
        quest.save()

        send_to_channel(
            game_id=self.game.id,
            game_event={
                "type": GameEventType.QUEST_UPDATE,
                "player_type": PlayerType.MASTER,
                "date": quest.date.isoformat(),
                "message": quest.message,
            },
        )

        send_mail.delay(
            subject=f"[{self.game}] The Master updated the quest.",
            message=f"The Master said:\n{quest.content}",
            from_email=self.game.master.user.email,
            recipient_list=get_players_emails(game=self.game),
        )

        return super().form_valid(form)


class AbilityCheckRequestView(
    UserPassesTestMixin,
    FormView,
    EventContextMixin,
):
    form_class = AbilityCheckRequestForm
    template_name = "game/ability_check_request.html"

    def test_func(self):
        return self.is_user_master()

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game.id,))

    def get_initial(self):
        initial = {"game": self.game}
        return initial

    def form_valid(self, form):
        ability_check_request = form.save(commit=False)
        ability_check_request.game = self.game
        ability_check_request.roll_type = RollType.ABILITY_CHECK
        ability_check_request.date = timezone.now()
        ability_check_request.message = f"[{ability_check_request.character.user}] \
            needs to perform a {ability_check_request.ability_type} ability check! \
            Difficulty: {ability_check_request.get_difficulty_klass_display()}."
        ability_check_request.save()

        send_to_channel(
            game_id=self.game.id,
            game_event={
                "type": GameEventType.ABILITY_CHECK_REQUEST,
                "player_type": PlayerType.MASTER,
                "date": ability_check_request.date.isoformat(),
                "message": ability_check_request.message,
            },
        )

        return super().form_valid(form)


class CombatCreate(
    UserPassesTestMixin,
    FormView,
    EventContextMixin,
):
    form_class = CombatCreateForm
    template_name = "game/combat_create.html"

    def test_func(self):
        return self.is_user_master()

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game.id,))

    def get_initial(self):
        initial = {"game": self.game}
        return initial

    def form_valid(self, form):
        combat = Combat(game=self.game)
        fighters = set()
        surpised_fighters = set()
        # The fighters must be created when they have been selected in the form.
        for fighter_field in form.fields:
            fighter = Fighter(
                combat=combat, character=Character.objects.get(name=fighter_field)
            )
            if CombatChoices.IS_FIGHTING in form.cleaned_data[fighter_field]:
                fighters.add(fighter.character.name)
                if CombatChoices.IS_SURPRISED in form.cleaned_data[fighter_field]:
                    surpised_fighters.add(fighter.character.name)
        # The combat initiation string must contain the fighters list and their
        # attributes.
        fighters_str = ""
        for fighter in fighters:
            fighters_str += fighter
            if fighter in surpised_fighters:
                fighters_str += " (surprised)"
        combat.message = f"Combat! {fighters_str}"
        combat.save()
        send_to_channel(
            game_id=self.game.id,
            game_event={
                "type": GameEventType.COMBAT_INITIATION,
                "player_type": PlayerType.MASTER,
                "date": combat.date.isoformat(),
                "message": combat.message,
            },
        )
        return super().form_valid(form)
