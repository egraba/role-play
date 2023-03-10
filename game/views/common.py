from django.http import Http404
from django.views.generic import DetailView, ListView

from game.models import Character, Event, Game, PendingAction, Tale


class IndexView(ListView):
    model = Game
    paginate_by = 10
    ordering = ["-start_date"]
    template_name = "game/index.html"


class GameView(ListView):
    model = Event
    paginate_by = 20
    ordering = ["-date"]
    template_name = "game/game.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            game_id = self.kwargs["game_id"]
            self.game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            raise Http404(f"Game [{game_id}] does not exist...", game_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        context["tale"] = Tale.objects.filter(game=self.game.id).last()
        context["character_list"] = Character.objects.filter(
            game=self.game.id
        ).order_by("name")
        context["pending_action_list"] = PendingAction.objects.filter(game=self.game.id)

        return context

    def get_queryset(self):
        return super().get_queryset().filter(game=self.game.id)


class DetailCharacterView(DetailView):
    model = Character
    template_name = "game/character.html"
