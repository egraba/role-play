import random

from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic

from game.forms import ChoiceForm, CreateGameForm, CreateTaleForm
from game.models import Character, Choice, DiceLaunch, Event, Game, PendingAction, Tale


class IndexView(generic.ListView):
    model = Game
    paginate_by = 10
    ordering = ["-start_date"]
    template_name = "game/index.html"


class CreateGameView(generic.FormView):
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


class GameView(generic.ListView):
    model = Event
    paginate_by = 20
    ordering = ["-date"]
    template_name = "game/game.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs["game_id"]
        try:
            context["game"] = Game.objects.get(pk=game_id)
            context["tale"] = Tale.objects.last()
            context["character_list"] = Character.objects.filter(game=game_id)
            context["pending_action_list"] = PendingAction.objects.filter(game=game_id)
        except Game.DoesNotExist:
            raise Http404(f"Game [{game_id}] does not exist...", game_id)
        return context

    def get_queryset(self):
        return super().get_queryset().filter(game=self.kwargs["game_id"])


class AddCharacterView(generic.ListView):
    model = Character
    paginate_by = 10
    ordering = ["-xp"]
    template_name = "game/addcharacter.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs["game_id"]
        try:
            context["game"] = Game.objects.get(pk=game_id)
        except Game.DoesNotExist:
            raise Http404(f"Game [{game_id}] does not exist...", game_id)
        return context

    def get_queryset(self):
        return super().get_queryset().filter(game=None)


class AddCharacterConfirmView(generic.UpdateView):
    model = Character
    fields = []
    template_name = "game/addcharacterconfirm.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.game_id = self.kwargs["game_id"]
        self.game = Game.objects.get(pk=self.game_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["game"] = self.game
        except Game.DoesNotExist:
            raise Http404(f"Game [{self.game_id}] does not exist...", self.game_id)
        return context

    def post(self, request, *args, **kwargs):
        character = self.get_object()
        character.game = self.game
        character.save()
        return HttpResponseRedirect(
            reverse(
                "game",
                args=(self.game_id,),
            )
        )


class CreateTaleView(generic.FormView):
    model = Tale
    fields = ["description"]
    template_name = "game/createtale.html"
    form_class = CreateTaleForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.game_id = self.kwargs["game_id"]
        self.game = Game.objects.get(pk=self.game_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        return context

    def post(self, request, *args, **kwargs):
        form = CreateTaleForm(request.POST)
        if form.is_valid():
            tale = Tale()
            tale.game = self.game
            tale.message = "The Master updated the story."
            tale.description = form.cleaned_data["description"]
            tale.save()
            return HttpResponseRedirect(reverse("game", args=(self.game_id,)))


class DiceLaunchView(generic.CreateView):
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


class ChoiceView(generic.FormView):
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


class DiceLaunchSuccessView(generic.DetailView):
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


class ChoiceSuccessView(generic.DetailView):
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
