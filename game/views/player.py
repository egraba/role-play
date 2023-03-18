import random

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, FormView

from game.forms import ChoiceForm, DiceLaunchForm
from game.models import Choice, DiceLaunch, PendingAction
from game.views.mixins import (
    CharacterContextMixin,
    EventConditionsMixin,
    GameContextMixin,
)


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


class ChoiceView(FormView, GameContextMixin, CharacterContextMixin):
    model = Choice
    fields = []
    template_name = "game/choice.html"
    form_class = ChoiceForm
    object = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.selection = None

    def post(self, request, *args, **kwargs):
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice = Choice()
            choice.game = self.game
            choice.character = self.character
            choice.selection = form.cleaned_data["selection"]
            choice.message = f"{self.character.name} made a choice: {choice.selection}!"
            choice.save()
            pending_action = PendingAction.objects.get(character=self.character)
            pending_action.delete()
            return HttpResponseRedirect(
                reverse(
                    "choice_success",
                    args=(
                        self.game_id,
                        self.character_id,
                        choice.pk,
                    ),
                )
            )


class ChoiceSuccessView(DetailView, GameContextMixin, CharacterContextMixin):
    model = Choice
    template_name = "game/success.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.choice = Choice.objects.get(pk=self.kwargs["action_id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["choice"] = self.choice
        return context

    def get_object(self):
        return Choice.objects.get(pk=self.kwargs.get("action_id"))

    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse("game", args=(self.game_id,)))
