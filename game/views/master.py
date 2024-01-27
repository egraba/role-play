from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, FormView, ListView, UpdateView
from django_fsm import TransitionNotAllowed

from character.models.character import Character
from character.views.mixins import CharacterContextMixin
from game.forms import (
    AbilityCheckRequestForm,
    DamageForm,
    HealingForm,
    QuestCreateForm,
    XpIncreaseForm,
)
from game.models.events import Damage, Event, Instruction, Quest, XpIncrease
from game.models.game import Player
from game.tasks import send_email
from game.utils.channels import EventType, send_to_chat
from game.utils.emails import get_players_emails
from game.views.mixins import (
    EventContextMixin,
    GameContextMixin,
    GameStatusControlMixin,
)


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
    fields = []
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
        send_email.delay(
            subject=f"The Master invited you to join [{self.game}].",
            message=f"{character}, the Master invited you to join [{self.game}].",
            from_email=self.game.master.user.email,
            recipient_list=[character.user.email],
        )
        return HttpResponseRedirect(reverse("game", args=(self.game.id,)))


class GameStartView(UserPassesTestMixin, GameStatusControlMixin):
    fields = []
    template_name = "game/game_start.html"

    def test_func(self):
        return self.is_user_master()

    def post(self, request, *args, **kwargs):
        game = self.get_object()
        try:
            game.start()
            game.save()
            cache.set(f"game{game.id}", game)
            event = Event.objects.create(game=game)
            event.date = timezone.now()
            event.message = "the game started."
            event.save()
            send_to_chat(game.id, EventType.MASTER_START, "")
        except TransitionNotAllowed:
            return HttpResponseRedirect(reverse("game-start-error", args=(game.id,)))
        return HttpResponseRedirect(game.get_absolute_url())


class GameStartErrorView(UserPassesTestMixin, GameStatusControlMixin):
    fields = []
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
        send_to_chat(self.game.id, EventType.MASTER_QUEST, "")
        send_email.delay(
            subject=f"[{self.game}] The Master updated the quest.",
            message=f"The Master said:\n{quest.content}",
            from_email=self.game.master.user.email,
            recipient_list=get_players_emails(game=self.game),
        )
        return super().form_valid(form)


class InstructionCreateView(UserPassesTestMixin, CreateView, EventContextMixin):
    model = Instruction
    fields = ["content"]
    template_name = "game/instruction_create.html"

    def test_func(self):
        return self.is_user_master()

    def get_success_url(self):
        return self.game.get_absolute_url()

    def form_valid(self, form):
        instruction = form.save(commit=False)
        instruction.game = self.game
        instruction.message = "The Master gave an instruction."
        instruction.save()
        return super().form_valid(form)


class XpIncreaseView(
    UserPassesTestMixin,
    FormView,
    EventContextMixin,
    CharacterContextMixin,
):
    model = XpIncrease
    form_class = XpIncreaseForm
    template_name = "game/xp.html"

    def test_func(self):
        return self.is_user_master()

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game.id,))

    def form_valid(self, form):
        xp_increase = form.save(commit=False)
        xp_increase.game = self.game
        xp_increase.character = self.character
        xp_increase.date = timezone.now()
        xp_increase.message = (
            f"{self.character} gained experience: +{xp_increase.xp} XP!"
        )
        xp_increase.save()
        self.character.xp += xp_increase.xp
        self.character.save()
        return super().form_valid(form)


class DamageView(
    UserPassesTestMixin,
    FormView,
    EventContextMixin,
    CharacterContextMixin,
):
    model = Damage
    form_class = DamageForm
    template_name = "game/damage.html"

    def test_func(self):
        return self.is_user_master()

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game.id,))

    def form_valid(self, form):
        damage = form.save(commit=False)
        damage.game = self.game
        damage.character = self.character
        damage.date = timezone.now()
        if damage.hp >= self.character.hp:
            damage.message = (
                f"{self.character} was hit: -{damage.hp} HP! {self.character} is dead."
            )
            # The player is removed from the game.
            Player.objects.get(character=self.character).delete()
            # The character is healed when remove from the game,
            # so that they can join another game.
            self.character.hp = self.character.max_hp
            self.character.save()
        else:
            damage.message = f"{self.character} was hit: -{damage.hp} HP!"
        damage.save()
        self.character.save()
        return super().form_valid(form)


class HealingView(
    UserPassesTestMixin,
    FormView,
    EventContextMixin,
    CharacterContextMixin,
):
    form_class = HealingForm
    template_name = "game/heal.html"

    def test_func(self):
        return self.is_user_master()

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game.id,))

    def form_valid(self, form):
        healing = form.save(commit=False)
        healing.game = self.game
        healing.character = self.character
        healing.date = timezone.now()
        # A character cannot have more HP that their max HP.
        max_healing = self.character.max_hp - self.character.hp
        if healing.hp > max_healing:
            healing.hp = max_healing
        healing.message = f"{self.character} was healed: +{healing.hp} HP!"
        healing.save()
        self.character.hp += healing.hp
        self.character.save()
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
        ability_check_request.date = timezone.now()
        ability_check_request.message = f"{ability_check_request.character} needs to perform \
            a {ability_check_request.ability_type} ability check! \
            Difficulty: {ability_check_request.get_difficulty_class_display()}."
        ability_check_request.save()
        send_to_chat(self.game.id, EventType.MASTER_ABILITY_CHECK, "")
        return super().form_valid(form)
