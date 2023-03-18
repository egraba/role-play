from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, FormView, ListView, UpdateView
from django_fsm import TransitionNotAllowed

from game.forms import (
    CreateGameForm,
    CreatePendingActionForm,
    CreateTaleForm,
    DamageForm,
    HealForm,
    IncreaseXpForm,
)
from game.models import Character, Damage, Game, PendingAction, Tale, XpIncrease
from game.views.mixins import CharacterContextMixin, GameContextMixin


class CreateGameView(PermissionRequiredMixin, FormView):
    permission_required = "game.add_game"
    template_name = "game/creategame.html"
    form_class = CreateGameForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        game = Game()
        game.name = form.cleaned_data["name"]
        game.save()
        tale = Tale()
        tale.game = game
        tale.message = "The Master created the story."
        tale.description = form.cleaned_data["description"]
        tale.save()
        return super().form_valid(form)


class AddCharacterView(PermissionRequiredMixin, ListView, GameContextMixin):
    permission_required = "game.change_character"
    model = Character
    paginate_by = 10
    ordering = ["-xp"]
    template_name = "game/addcharacter.html"

    def get_queryset(self):
        return super().get_queryset().filter(game=None)


class AddCharacterConfirmView(PermissionRequiredMixin, UpdateView, GameContextMixin):
    permission_required = "game.change_character"
    model = Character
    fields = []
    template_name = "game/addcharacterconfirm.html"

    def post(self, request, *args, **kwargs):
        character = self.get_object()
        character.game = self.game
        character.save()
        return HttpResponseRedirect(
            reverse(
                "game",
                args=(self.game.id,),
            )
        )


class StartGameView(PermissionRequiredMixin, UpdateView):
    permission_required = "game.change_game"
    model = Game
    fields = []
    template_name = "game/startgame.html"

    def post(self, request, *args, **kwargs):
        game = self.get_object()
        try:
            game.start()
            game.save()
        except TransitionNotAllowed:
            raise PermissionDenied
        return HttpResponseRedirect(
            reverse(
                "game",
                args=(game.id,),
            )
        )


class EndGameView(PermissionRequiredMixin, UpdateView):
    permission_required = "game.change_game"
    model = Game
    fields = []
    template_name = "game/endgame.html"

    def post(self, request, *args, **kwargs):
        game = self.get_object()
        game.end()
        game.save()
        return HttpResponseRedirect(
            reverse(
                "game",
                args=(game.id,),
            )
        )


class CreateTaleView(PermissionRequiredMixin, FormView, GameContextMixin):
    permission_required = "game.add_tale"
    model = Tale
    fields = ["description"]
    template_name = "game/createtale.html"
    form_class = CreateTaleForm

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game.id,))

    def form_valid(self, form):
        tale = Tale()
        tale.game = self.game
        tale.message = "The Master updated the story."
        tale.description = form.cleaned_data["description"]
        tale.save()
        return super().form_valid(form)


class CreatePendingActionView(
    PermissionRequiredMixin, CreateView, GameContextMixin, CharacterContextMixin
):
    permission_required = "game.add_pendingaction"
    model = PendingAction
    form_class = CreatePendingActionForm
    template_name = "game/creatependingaction.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        pending_action_list = PendingAction.objects.filter(character=self.character)
        if len(pending_action_list) > 0:
            raise PermissionDenied

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game_id,))

    def form_valid(self, form):
        pending_action = form.save(commit=False)
        pending_action.game = self.game
        pending_action.character = self.character
        pending_action.date = timezone.now()
        pending_action.message = f"{self.character} needs to perform an action: {pending_action.get_action_type_display()}"
        pending_action.save()
        return super().form_valid(form)


class IncreaseXpView(
    PermissionRequiredMixin, FormView, GameContextMixin, CharacterContextMixin
):
    permission_required = "game.add_xpincrease"
    model = XpIncrease
    form_class = IncreaseXpForm
    template_name = "game/xp.html"

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game_id,))

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
    PermissionRequiredMixin, FormView, GameContextMixin, CharacterContextMixin
):
    permission_required = "game.add_damage"
    model = Damage
    form_class = DamageForm
    template_name = "game/damage.html"

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game_id,))

    def form_valid(self, form):
        damage = form.save(commit=False)
        damage.game = self.game
        damage.character = self.character
        damage.date = timezone.now()
        damage.message = f"{self.character} was hit: -{damage.hp} HP!"
        damage.save()
        self.character.hp -= damage.hp
        self.character.save()
        return super().form_valid(form)


class HealView(
    PermissionRequiredMixin, FormView, GameContextMixin, CharacterContextMixin
):
    permission_required = "game.add_healing"
    form_class = HealForm
    template_name = "game/heal.html"

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game_id,))

    def form_valid(self, form):
        healing = form.save(commit=False)
        healing.game = self.game
        healing.character = self.character
        healing.date = timezone.now()
        healing.message = f"{self.character} was healed: +{healing.hp} HP!"
        healing.save()
        if healing.hp + self.character.hp <= self.character.max_hp:
            self.character.hp += healing.hp
        else:
            self.character.hp = self.character.max_hp
        self.character.save()
        return super().form_valid(form)
