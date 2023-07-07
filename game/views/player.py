import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

import game.forms as gforms
import game.models as gmodels
import game.views.mixins as gmixins


class DiceLaunchView(
    LoginRequiredMixin,
    CreateView,
    gmixins.EventContextMixin,
    gmixins.CharacterContextMixin,
):
    model = gmodels.DiceLaunch
    form_class = gforms.DiceLaunchForm
    template_name = "game/dice.html"

    def get_success_url(self):
        return reverse_lazy(
            "dicelaunch-success",
            args=(
                self.game.id,
                self.character.id,
                self.object.id,
            ),
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
        pending_action = gmodels.PendingAction.objects.get(character=self.character)
        pending_action.delete()
        return super().form_valid(form)


class DiceLaunchSuccessView(
    LoginRequiredMixin,
    DetailView,
    gmixins.GameContextMixin,
    gmixins.CharacterContextMixin,
):
    model = gmodels.DiceLaunch
    template_name = "game/success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dice_launch"] = self.get_object()
        return context

    def get_object(self):
        return gmodels.DiceLaunch.objects.get(pk=self.kwargs.get("action_id"))


class ChoiceView(
    LoginRequiredMixin,
    CreateView,
    gmixins.EventContextMixin,
    gmixins.CharacterContextMixin,
):
    model = gmodels.Choice
    form_class = gforms.ChoiceForm
    template_name = "game/choice.html"

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game.id,))

    def form_valid(self, form):
        choice = form.save(commit=False)
        choice.game = self.game
        choice.character = self.character
        choice.message = f"{self.character.name} made a choice: {choice.selection}."
        choice.save()
        pending_action = gmodels.PendingAction.objects.get(character=self.character)
        pending_action.delete()
        return super().form_valid(form)
