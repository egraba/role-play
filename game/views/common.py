from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from game.models import Character, Event, Game, PendingAction, Tale
from game.views.mixins import GameContextMixin


class IndexView(ListView):
    model = Game
    paginate_by = 10
    ordering = ["-start_date"]
    template_name = "game/index.html"


class GameView(LoginRequiredMixin, ListView, GameContextMixin):
    model = Event
    paginate_by = 20
    ordering = ["-date"]
    template_name = "game/game.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tale"] = Tale.objects.filter(game=self.game.id).last()
        context["character_list"] = Character.objects.filter(
            game=self.game.id
        ).order_by("name")
        try:
            player = Character.objects.get(user=self.request.user)
            context["player"] = player
            context["pending_action"] = PendingAction.objects.filter(
                game=self.game.id, character=player
            ).get()
        except Character.DoesNotExist:
            pass
        return context

    def get_queryset(self):
        return super().get_queryset().filter(game=self.game.id)


class DetailCharacterView(DetailView):
    model = Character
    template_name = "game/character.html"
