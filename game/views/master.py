from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, FormView, ListView, UpdateView
from django_fsm import TransitionNotAllowed

import game.forms as gforms
import game.models as gmodels
import game.views.mixins as gmixins


class CreateGameView(PermissionRequiredMixin, FormView):
    permission_required = "game.add_game"
    template_name = "game/creategame.html"
    form_class = gforms.CreateGameForm

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game.id,))

    def form_valid(self, form):
        self.game = gmodels.Game()
        self.game.name = form.cleaned_data["name"]
        self.game.user = self.request.user
        self.game.save()
        tale = gmodels.Tale()
        tale.game = self.game
        tale.message = "The Master created the story."
        tale.description = form.cleaned_data["description"]
        tale.save()
        return super().form_valid(form)


class AddCharacterView(PermissionRequiredMixin, ListView, gmixins.GameContextMixin):
    permission_required = "game.change_character"
    model = gmodels.Character
    paginate_by = 10
    ordering = ["-xp"]
    template_name = "game/addcharacter.html"

    def get_queryset(self):
        return super().get_queryset().filter(game=None)


class AddCharacterConfirmView(
    PermissionRequiredMixin, UpdateView, gmixins.GameContextMixin
):
    permission_required = "game.change_character"
    model = gmodels.Character
    fields = []
    template_name = "game/addcharacterconfirm.html"

    def post(self, request, *args, **kwargs):
        character = self.get_object()
        character.game = self.game
        character.save()
        event = gmodels.Event.objects.create(game=self.game)
        event.date = timezone.now()
        event.message = f"{character} was added to the game."
        event.save()
        return HttpResponseRedirect(reverse("game", args=(self.game.id,)))


class StartGameView(PermissionRequiredMixin, UpdateView):
    permission_required = "game.change_game"
    model = gmodels.Game
    fields = []
    template_name = "game/startgame.html"

    def post(self, request, *args, **kwargs):
        game = self.get_object()
        try:
            game.start()
            game.save()
            event = gmodels.Event.objects.create(game=game)
            event.date = timezone.now()
            event.message = "The game started."
            event.save()
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
    model = gmodels.Game
    fields = []
    template_name = "game/endgame.html"

    def post(self, request, *args, **kwargs):
        game = self.get_object()
        game.end()
        game.save()
        event = gmodels.Event.objects.create(game=game)
        event.date = timezone.now()
        event.message = "The game ended."
        event.save()
        return HttpResponseRedirect(
            reverse(
                "game",
                args=(game.id,),
            )
        )


class CreateTaleView(PermissionRequiredMixin, FormView, gmixins.EventConditionsMixin):
    permission_required = "game.add_tale"
    model = gmodels.Tale
    fields = ["description"]
    template_name = "game/createtale.html"
    form_class = gforms.CreateTaleForm

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game.id,))

    def form_valid(self, form):
        tale = gmodels.Tale()
        tale.game = self.game
        tale.message = "The Master updated the story."
        tale.description = form.cleaned_data["description"]
        tale.save()
        return super().form_valid(form)


class CreatePendingActionView(
    PermissionRequiredMixin,
    CreateView,
    gmixins.EventConditionsMixin,
    gmixins.CharacterContextMixin,
):
    permission_required = "game.add_pendingaction"
    model = gmodels.PendingAction
    form_class = gforms.CreatePendingActionForm
    template_name = "game/creatependingaction.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        pending_action_list = gmodels.PendingAction.objects.filter(
            character=self.character
        )
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
    PermissionRequiredMixin,
    FormView,
    gmixins.EventConditionsMixin,
    gmixins.CharacterContextMixin,
):
    permission_required = "game.add_xpincrease"
    model = gmodels.XpIncrease
    form_class = gforms.IncreaseXpForm
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
    PermissionRequiredMixin,
    FormView,
    gmixins.EventConditionsMixin,
    gmixins.CharacterContextMixin,
):
    permission_required = "game.add_damage"
    model = gmodels.Damage
    form_class = gforms.DamageForm
    template_name = "game/damage.html"

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game_id,))

    def form_valid(self, form):
        damage = form.save(commit=False)
        damage.game = self.game
        damage.character = self.character
        damage.date = timezone.now()
        if damage.hp >= self.character.hp:
            damage.message = (
                f"{self.character} was hit: -{damage.hp} HP! {self.character} is dead."
            )
            self.character.game = None  # The character is out of the game.
            self.character.hp = (
                self.character.max_hp
            )  # The character is healed when out.
            self.character.save()
        else:
            damage.message = f"{self.character} was hit: -{damage.hp} HP!"
        damage.save()
        self.character.save()
        return super().form_valid(form)


class HealView(
    PermissionRequiredMixin,
    FormView,
    gmixins.EventConditionsMixin,
    gmixins.CharacterContextMixin,
):
    permission_required = "game.add_healing"
    form_class = gforms.HealForm
    template_name = "game/heal.html"

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game_id,))

    def form_valid(self, form):
        healing = form.save(commit=False)
        healing.game = self.game
        healing.character = self.character
        healing.date = timezone.now()
        max_healing = self.character.max_hp - self.character.hp
        if healing.hp > max_healing:
            healing.hp = max_healing
        healing.message = f"{self.character} was healed: +{healing.hp} HP!"
        healing.save()
        self.character.hp += healing.hp
        self.character.save()
        return super().form_valid(form)
