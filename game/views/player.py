import random

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, FormView

from game.forms import ChoiceForm
from game.models import Character, Choice, DiceLaunch, Game, PendingAction


class DiceLaunchView(CreateView):
    model = Choice
    fields = []
    template_name = "game/dice.html"
    object = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.game_id = self.kwargs["game_id"]
        self.game = Game.objects.get(pk=self.game_id)
        self.character_id = self.kwargs["character_id"]
        self.character = Character.objects.get(pk=self.character_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        context["character"] = self.character
        return context

    def post(self, request, *args, **kwargs):
        dice_launch = DiceLaunch()
        dice_launch.game = self.game
        dice_launch.character = self.character
        dice_launch.score = random.randint(1, 20)
        dice_launch.message = (
            f"{self.character.name} launched a dice: score is {dice_launch.score}!"
        )
        dice_launch.save()
        pending_action = PendingAction.objects.get(character=self.character)
        pending_action.delete()
        return HttpResponseRedirect(
            reverse(
                "dice_success",
                args=(
                    self.game_id,
                    self.character_id,
                    dice_launch.pk,
                ),
            )
        )


class ChoiceView(FormView):
    model = Choice
    fields = []
    template_name = "game/choice.html"
    form_class = ChoiceForm
    object = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.game_id = self.kwargs["game_id"]
        self.game = Game.objects.get(pk=self.game_id)
        self.character_id = self.kwargs["character_id"]
        self.character = Character.objects.get(pk=self.character_id)
        self.selection = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        context["character"] = self.character
        return context

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


class DiceLaunchSuccessView(DetailView):
    model = Choice
    template_name = "game/success.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.game_id = self.kwargs["game_id"]
        self.game = Game.objects.get(pk=self.game_id)
        self.character_id = self.kwargs["character_id"]
        self.character = Character.objects.get(pk=self.character_id)
        self.dice_launch = DiceLaunch.objects.get(pk=self.kwargs["action_id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        context["character"] = self.character
        context["dice_launch"] = self.dice_launch
        return context

    def get_object(self):
        return DiceLaunch.objects.get(pk=self.kwargs.get("action_id"))

    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse("game", args=(self.game_id,)))


class ChoiceSuccessView(DetailView):
    model = Choice
    template_name = "game/success.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.game_id = self.kwargs["game_id"]
        self.game = Game.objects.get(pk=self.game_id)
        self.character_id = self.kwargs["character_id"]
        self.character = Character.objects.get(pk=self.character_id)
        self.choice = Choice.objects.get(pk=self.kwargs["action_id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        context["character"] = self.character
        context["choice"] = self.choice
        return context

    def get_object(self):
        return Choice.objects.get(pk=self.kwargs.get("action_id"))

    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse("game", args=(self.game_id,)))
