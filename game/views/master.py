from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import generic

from game.forms import CreateGameForm, CreateTaleForm
from game.models import Character, Game, Tale


class CreateGameView(generic.FormView):
    template_name = "game/creategame.html"
    form_class = CreateGameForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        game = Game()
        game.name = form.cleaned_data["name"]
        game.status = "P"
        game.save()
        tale = Tale()
        tale.game = game
        tale.message = "The Master created the story."
        tale.description = form.cleaned_data["description"]
        tale.save()
        return super().form_valid(form)


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


class StartGameView(generic.UpdateView):
    model = Game
    fields = []
    template_name = "game/startgame.html"

    def post(self, request, *args, **kwargs):
        game = self.get_object()
        character_list = Character.objects.filter(game=game)
        if len(character_list) >= 2:
            game.start_date = timezone.now()
            game.status = "S"
            game.save()
        else:
            raise PermissionDenied("A game must contain at least 2 players...")
        return HttpResponseRedirect(
            reverse(
                "game",
                args=(game.id,),
            )
        )


class EndGameView(generic.UpdateView):
    model = Game
    fields = []
    template_name = "game/endgame.html"

    def post(self, request, *args, **kwargs):
        game = self.get_object()
        if game.status == "S":
            game.end_date = timezone.now()
            game.status = "E"
            game.save()
        else:
            raise PermissionDenied("A game must have been started to be ended...")
        return HttpResponseRedirect(
            reverse(
                "game",
                args=(game.id,),
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
