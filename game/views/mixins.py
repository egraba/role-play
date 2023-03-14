from django.http import Http404
from django.views.generic import View
from django.views.generic.list import ContextMixin

from game.models import Game


class GameContextMixin(ContextMixin, View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.game_id = self.kwargs["game_id"]
            self.game = Game.objects.get(id=self.game_id)
        except Game.DoesNotExist:
            raise Http404(f"Game [{self.game_id}] does not exist...")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        return context
