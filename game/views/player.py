import random

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

from game.forms import ChoiceForm, CreateCharacterForm, DiceLaunchForm
from game.models import Character, Choice, DiceLaunch, PendingAction
from game.views.mixins import (
    CharacterContextMixin,
    EventConditionsMixin,
    GameContextMixin,
)


class CreateCharacterView(PermissionRequiredMixin, CreateView):
    permission_required = "game.add_character"
    model = Character
    form_class = CreateCharacterForm
    template_name = "game/createcharacter.html"

    def get_success_url(self):
        return reverse_lazy("character-detail", args=(self.object.id,))


class DiceLaunchView(
    PermissionRequiredMixin, CreateView, EventConditionsMixin, CharacterContextMixin
):
    permission_required = "game.add_dicelaunch"
    model = DiceLaunch
    form_class = DiceLaunchForm
    template_name = "game/dice.html"

    def get_success_url(self):
        return reverse_lazy(
            "dicelaunch-success", args=(self.game.id, self.character.id, self.object.id)
        )

    def form_valid(self, form):
        dice_launch = form.save(commit=False)
        dice_launch.game = self.game
        dice_launch.character = self.character
        dice_launch.score = random.randint(1, 20)
        dice_launch.message = (
            f"{self.character} launched a dice: score is {dice_launch.score}!"
        )
        dice_launch.save()
        pending_action = PendingAction.objects.get(character=self.character)
        pending_action.delete()
        return super().form_valid(form)


class DiceLaunchSuccessView(DetailView, GameContextMixin, CharacterContextMixin):
    model = DiceLaunch
    template_name = "game/success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dice_launch"] = self.get_object()
        return context

    def get_object(self):
        return DiceLaunch.objects.get(pk=self.kwargs.get("action_id"))


class ChoiceView(
    PermissionRequiredMixin, CreateView, EventConditionsMixin, CharacterContextMixin
):
    permission_required = "game.add_choice"
    model = Choice
    form_class = ChoiceForm
    template_name = "game/choice.html"

    def get_success_url(self):
        return reverse_lazy(
            "game",
            args=(self.game.id,),
        )

    def form_valid(self, form):
        choice = form.save(commit=False)
        choice.game = self.game
        choice.character = self.character
        choice.message = f"{self.character.name} made a choice: {choice.selection}."
        choice.save()
        pending_action = PendingAction.objects.get(character=self.character)
        pending_action.delete()
        return super().form_valid(form)
