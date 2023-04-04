from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404
from django.views.generic import View
from django.views.generic.list import ContextMixin

import game.models as gmodels


class GameContextMixin(ContextMixin, View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        game_id = self.kwargs["game_id"]
        try:
            self.game = gmodels.Game.objects.get(id=game_id)
        except ObjectDoesNotExist:
            raise Http404(f"Game [{game_id}] does not exist...")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        return context


class CharacterContextMixin(ContextMixin, View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        character_id = self.kwargs["character_id"]
        try:
            self.character = gmodels.Character.objects.get(id=character_id)
        except ObjectDoesNotExist:
            raise Http404(f"Character [{character_id}] does not exist...")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["character"] = self.character
        return context


class EventConditionsMixin(GameContextMixin, View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if not self.game.is_ongoing():
            raise PermissionDenied()
        else:
            pass
