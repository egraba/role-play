from django.http import Http404
from django.views import generic

from game.models import Character, Event, Game, PendingAction, Tale


class IndexView(generic.ListView):
    model = Game
    paginate_by = 10
    ordering = ["-start_date"]
    template_name = "game/index.html"


class GameView(generic.ListView):
    model = Event
    paginate_by = 20
    ordering = ["-date"]
    template_name = "game/game.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.game_id = self.kwargs["game_id"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["game"] = Game.objects.get(pk=self.game_id)
            context["tale"] = Tale.objects.filter(game=self.game_id).last()
            context["character_list"] = Character.objects.filter(game=self.game_id)
            context["pending_action_list"] = PendingAction.objects.filter(
                game=self.game_id
            )
        except Game.DoesNotExist:
            raise Http404(f"Game [{self.game_id}] does not exist...", self.game_id)
        return context

    def get_queryset(self):
        return super().get_queryset().filter(game=self.game_id)
