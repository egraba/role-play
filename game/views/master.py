from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, ListView, UpdateView
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from viewflow.fsm import TransitionNotAllowed

from character.models.character import Character
from user.models import User

from ..constants.combat import FighterAttributeChoices
from ..constants.events import RollType
from ..flows import GameFlow
from ..forms import AbilityCheckRequestForm, CombatCreateForm, QuestCreateForm
from ..models.combat import Combat, Fighter
from ..models.events import (
    UserInvitation,
    CombatInitialization,
    CombatInitiativeRequest,
    GameStart,
    QuestUpdate,
)
from ..models.game import Player, Quest
from ..tasks import send_mail
from ..utils.cache import game_key
from ..utils.channels import send_to_channel
from ..utils.emails import get_players_emails
from ..views.mixins import EventContextMixin, GameContextMixin, GameStatusControlMixin


class UserInviteView(UserPassesTestMixin, ListView, GameContextMixin):
    model = User
    paginate_by = 10
    template_name = "game/user_invite.html"

    def test_func(self):
        return self.is_user_master()

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(character__isnull=False, player__isnull=True)
            .order_by("username")
        )


class UserInviteConfirmView(UserPassesTestMixin, UpdateView, GameContextMixin):
    model = User
    fields = []  # type: list[str]
    template_name = "game/user_invite_confirm.html"

    def test_func(self):
        return self.is_user_master()

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        UserInvitation.objects.create(user=user, game=self.game)
        Player.objects.create(user=user, game=self.game, character=user.character)
        send_mail.delay(
            subject=f"The Master invited you to join [{self.game}].",
            message=f"{user}, the Master invited you to join [{self.game}].",
            from_email=self.game.master.user.email,
            recipient_list=[user.email],
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
            game_start = GameStart.objects.create(game=game)
            send_to_channel(game_start)
        except TransitionNotAllowed:
            return HttpResponseRedirect(reverse("game-start-error", args=(game.id,)))
        return HttpResponseRedirect(game.get_absolute_url())


class GameStartErrorView(UserPassesTestMixin, GameStatusControlMixin):
    fields = []  # type: list[str]
    template_name = "game/game_start_error.html"

    def test_func(self):
        return self.is_user_master()


class QuestCreateView(UserPassesTestMixin, FormView, EventContextMixin):
    model = QuestUpdate
    fields = ["description"]
    template_name = "game/quest_create.html"
    form_class = QuestCreateForm

    def test_func(self):
        return self.is_user_master()

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game.id,))

    def form_valid(self, form):
        quest = Quest.objects.create(
            environment=form.cleaned_data["environment"], game=self.game
        )
        quest_update = QuestUpdate.objects.create(game=self.game, quest=quest)
        send_to_channel(quest_update)
        send_mail.delay(
            subject=f"[{self.game}] The Master updated the quest.",
            message=f"The Master said:\n{quest.environment}",
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
        ability_check_request.save()
        send_to_channel(ability_check_request)
        return super().form_valid(form)


class CombatCreateView(
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
        # Combat can be created here as the form has been validated to contain fighters.
        combat = Combat.objects.create(game=self.game)
        # Fighters must be created only for selected characters.
        for fighter_field in form.fields:
            if FighterAttributeChoices.IS_FIGHTING in form.cleaned_data[fighter_field]:
                is_surprised = False
                if (
                    FighterAttributeChoices.IS_SURPRISED
                    in form.cleaned_data[fighter_field]
                ):
                    is_surprised = True
                Fighter.objects.create(
                    character=Character.objects.get(name=fighter_field),
                    is_surprised=is_surprised,
                    combat=combat,
                )
        combat_init = CombatInitialization.objects.create(game=self.game, combat=combat)
        send_to_channel(combat_init)
        for fighter in combat.fighter_set.all():
            initiative_request = CombatInitiativeRequest.objects.create(
                game=self.game, fighter=fighter
            )
            send_to_channel(initiative_request)
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=2,
                period=IntervalSchedule.SECONDS,
            )
            PeriodicTask.objects.get_or_create(
                interval=schedule,
                name=f"game{self.game.id}: Check if combat roll initiative is complete",
                task="game.tasks.check_combat_roll_initiative_complete",
            )
        return super().form_valid(form)
