from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, FormView, ListView, UpdateView
from django_fsm import TransitionNotAllowed

import character.models as cmodels
import game.forms as gforms
import game.models as gmodels
import game.utils as gutils
import game.views.mixins as gmixins


class CharacterInviteView(UserPassesTestMixin, ListView, gmixins.GameContextMixin):
    model = cmodels.Character
    paginate_by = 10
    ordering = ["-xp"]
    template_name = "game/character_invite.html"

    def test_func(self):
        return self.is_user_master()

    def get_queryset(self):
        return super().get_queryset().filter(player__game=None)


class CharacterInviteConfirmView(
    UserPassesTestMixin, UpdateView, gmixins.GameContextMixin
):
    model = cmodels.Character
    fields = []
    template_name = "game/character_invite_confirm.html"

    def test_func(self):
        return self.is_user_master()

    def post(self, request, *args, **kwargs):
        character = self.get_object()
        gmodels.Player.objects.create(character=character, game=self.game)
        event = gmodels.Event.objects.create(game=self.game)
        event.date = timezone.now()
        event.message = f"{character} was added to the game."
        event.save()
        send_mail(
            f"The Master invited you to join. [{self.game}]",
            f"{character}, the Master you to join. [{self.game}]",
            self.game.master.user.email,
            [character.user.email],
        )
        return HttpResponseRedirect(reverse("game", args=(self.game.id,)))


class GameStartView(UserPassesTestMixin, gmixins.GameStatusControlMixin):
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
            event = gmodels.Event.objects.create(game=game)
            event.date = timezone.now()
            event.message = "the game started."
            event.save()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"game_{game.id}_events",
                {"type": "master.start", "content": ""},
            )
        except TransitionNotAllowed:
            return HttpResponseRedirect(reverse("game-start-error", args=(game.id,)))
        return HttpResponseRedirect(game.get_absolute_url())


class GameStartErrorView(UserPassesTestMixin, gmixins.GameStatusControlMixin):
    fields = []
    template_name = "game/game_start_error.html"

    def test_func(self):
        return self.is_user_master()


class QuestCreateView(UserPassesTestMixin, FormView, gmixins.EventContextMixin):
    model = gmodels.Quest
    fields = ["description"]
    template_name = "game/quest_create.html"
    form_class = gforms.CreateQuestForm

    def test_func(self):
        return self.is_user_master()

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game.id,))

    def form_valid(self, form):
        quest = gmodels.Quest()
        quest.game = self.game
        quest.message = "the Master updated the story."
        quest.content = form.cleaned_data["content"]
        quest.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"game_{self.game.id}_events",
            {"type": "master.quest", "content": ""},
        )
        send_mail(
            f"[{self.game}] The Master updated the quest.",
            f"The Master said:\n{quest.content}",
            gutils.get_master_email(self.game.master.user.username),
            gutils.get_players_emails(game=self.game),
        )
        return super().form_valid(form)


class InstructionCreateView(UserPassesTestMixin, CreateView, gmixins.EventContextMixin):
    model = gmodels.Instruction
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
    gmixins.EventContextMixin,
    gmixins.CharacterContextMixin,
):
    model = gmodels.XpIncrease
    form_class = gforms.IncreaseXpForm
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
    gmixins.EventContextMixin,
    gmixins.CharacterContextMixin,
):
    model = gmodels.Damage
    form_class = gforms.DamageForm
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
            gmodels.Player.objects.get(character=self.character).delete()
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
    gmixins.EventContextMixin,
    gmixins.CharacterContextMixin,
):
    form_class = gforms.HealForm
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
