import random

from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from game.forms import ChoiceForm, NewGameForm, NewNarrativeForm
from game.models import Character, Choice, DiceLaunch, Game, Narrative, PendingAction


class IndexView(generic.ListView):
    template_name = "game/index.html"

    def get_queryset(self):
        return Game.objects.all()


class NewGameView(generic.FormView):
    model = Game
    fields = ["name"]
    template_name = "game/newgame.html"
    form_class = NewGameForm

    def post(self, request, *args, **kwargs):
        form = NewGameForm(request.POST)
        if form.is_valid():
            game = Game()
            game.name = form.cleaned_data["name"]
            game.save()
            return HttpResponseRedirect(
                reverse(
                    "index",
                )
            )


class GameView(generic.ListView):
    model = Game
    template_name = "game/game.html"

    def setup(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        game_id = self.kwargs["game_id"]
        try:
            self.game = Game.objects.get(pk=game_id)
            self.character_list = Character.objects.filter(game=game_id)
            self.narrative_list = Narrative.objects.filter(game=game_id)
            self.pending_action_list = PendingAction.objects.filter(game=game_id)
        except Game.DoesNotExist:
            raise Http404(f"Game [{game_id}] does not exist...", game_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        context["character_list"] = self.character_list
        context["narrative_list"] = self.narrative_list
        context["pending_action_list"] = self.pending_action_list
        return context


class NewNarrativeView(generic.FormView):
    model = Narrative
    fields = ["message"]
    template_name = "game/newnarrative.html"
    form_class = NewNarrativeForm

    def setup(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.game_id = self.kwargs["game_id"]
        self.game = Game.objects.get(pk=self.game_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        return context

    def post(self, request, *args, **kwargs):
        form = NewNarrativeForm(request.POST)
        if form.is_valid():
            narrative = Narrative()
            narrative.game = self.game
            narrative.message = form.cleaned_data["message"]
            narrative.save()
            return HttpResponseRedirect(reverse("game", args=(self.game_id,)))


class DiceLaunchView(generic.CreateView):
    model = DiceLaunch
    fields = []
    template_name = "game/dice.html"
    object = None

    def setup(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
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


class ChoiceView(generic.FormView):
    model = Choice
    fields = []
    template_name = "game/choice.html"
    form_class = ChoiceForm
    object = None

    def setup(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
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


class DiceLaunchSuccessView(generic.DetailView):
    model = DiceLaunch
    template_name = "game/success.html"

    def setup(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
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


class ChoiceSuccessView(generic.DetailView):
    model = Choice
    template_name = "game/success.html"

    def setup(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
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
