from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, FormView, ListView, UpdateView
from django_eventstream import send_event
from django_fsm import TransitionNotAllowed

import character.models as cmodels
import game.forms as gforms
import game.models as gmodels
import game.utils as gutils
import game.views.mixins as gmixins


class InviteCharacterView(UserPassesTestMixin, ListView, gmixins.GameContextMixin):
    model = cmodels.Character
    paginate_by = 10
    ordering = ["-xp"]
    template_name = "game/invitecharacter.html"

    def test_func(self):
        return self.is_user_master()

    def get_queryset(self):
        return super().get_queryset().filter(player__game=None)


class InviteCharacterConfirmView(
    UserPassesTestMixin, UpdateView, gmixins.GameContextMixin
):
    model = cmodels.Character
    fields = []
    template_name = "game/invitecharacterconfirm.html"

    def test_func(self):
        return self.is_user_master()

    def post(self, request, *args, **kwargs):
        character = self.get_object()
        player = gmodels.Player.objects.get(character=character)
        player.game = self.game
        player.save()
        event = gmodels.Event.objects.create(game=self.game)
        event.date = timezone.now()
        event.message = f"{character} was added to the game."
        event.save()
        return HttpResponseRedirect(reverse("game", args=(self.game.id,)))


class StartGameView(UserPassesTestMixin, gmixins.GameStatusControlMixin):
    fields = []
    template_name = "game/startgame.html"

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
            event.message = "The game started."
            event.save()
        except TransitionNotAllowed:
            return HttpResponseRedirect(reverse("game-start-error", args=(game.id,)))
        return HttpResponseRedirect(reverse("game", args=(game.id,)))


class StartGameErrorView(UserPassesTestMixin, gmixins.GameStatusControlMixin):
    fields = []
    template_name = "game/startgameerror.html"

    def test_func(self):
        return self.is_user_master()


class EndGameView(UserPassesTestMixin, gmixins.GameStatusControlMixin):
    fields = []
    template_name = "game/endgame.html"

    def test_func(self):
        return self.is_user_master()

    def post(self, request, *args, **kwargs):
        game = self.get_object()
        game.end()
        game.save()
        cache.set(f"game{game.id}", game)
        event = gmodels.Event.objects.create(game=game)
        event.date = timezone.now()
        event.message = "The game ended."
        event.save()
        return HttpResponseRedirect(reverse("game", args=(game.id,)))


class CreateTaleView(UserPassesTestMixin, FormView, gmixins.EventContextMixin):
    model = gmodels.Tale
    fields = ["description"]
    template_name = "game/createtale.html"
    form_class = gforms.CreateTaleForm

    def test_func(self):
        return self.is_user_master()

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game.id,))

    def form_valid(self, form):
        tale = gmodels.Tale()
        tale.game = self.game
        tale.message = "The Master updated the story."
        tale.content = form.cleaned_data["content"]
        tale.save()
        send_mail(
            f"[{self.game}] The Master updated the story.",
            f"The Master said:\n{tale.content}",
            gutils.get_master_email(self.game.master.username),
            gutils.get_players_emails(game=self.game),
        )
        send_event("game", "message", {"game": self.game.id, "refresh": "tale"})
        return super().form_valid(form)


class CreatePendingActionView(
    UserPassesTestMixin,
    CreateView,
    gmixins.EventContextMixin,
    gmixins.CharacterContextMixin,
):
    model = gmodels.PendingAction
    form_class = gforms.CreatePendingActionForm
    template_name = "game/creatependingaction.html"

    def test_func(self):
        return self.is_user_master()

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            gmodels.PendingAction.objects.get(character=self.character)
            raise PermissionDenied
        except ObjectDoesNotExist:
            pass

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game.id,))

    def form_valid(self, form):
        pending_action = form.save(commit=False)
        pending_action.game = self.game
        pending_action.character = self.character
        pending_action.date = timezone.now()
        pending_action.message = f"{self.character} needs to perform an action: {pending_action.get_action_type_display()}"
        pending_action.save()
        return super().form_valid(form)


class IncreaseXpView(
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
            # The player removed from the game.
            player = gmodels.Player.objects.get(character=self.character)
            player.game = None
            player.save()
            # The character is healed when remove from the game,
            # so that they can join another game.
            self.character.hp = self.character.max_hp
            self.character.save()
        else:
            damage.message = f"{self.character} was hit: -{damage.hp} HP!"
        damage.save()
        self.character.save()
        return super().form_valid(form)


class HealView(
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
