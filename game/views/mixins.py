from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404
from django.views.generic import UpdateView, View
from django.views.generic.edit import FormMixin
from django.views.generic.list import ContextMixin

from ..models.game import Game
from ..utils.cache import game_key
from ..flows import GameFlow


class GameContextMixin(ContextMixin, View):
    """
    Mixin class that provides game object and context.

    Attributes:
        game (Game): Game instance.
    """

    def is_user_master(self) -> bool:
        """Return True if the logged user is the game master."""
        return self.request.user == self.game.master.user

    def is_user_player(self):
        """Return True if the logged user is a player of the game."""
        try:
            self.game.player_set.get(character__user=self.request.user)
            return True
        except ObjectDoesNotExist:
            return False

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        game_id = self.kwargs["game_id"]
        try:
            self.game = cache.get_or_set(
                game_key(game_id), Game.objects.get(id=game_id)
            )
        except ObjectDoesNotExist as e:
            raise Http404(f"Game of {game_id=} not found") from e
        if not self.is_user_master() and not self.is_user_player():
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        return context


class GameStatusControlMixin(UpdateView):
    """
    Mixin class that provides game object, for views inheriting from UpdateViews.

    Attributes:
        model (Game): Game instance.
    """

    model = Game

    def is_user_master(self):
        """Return True if the logged user is the game master."""
        return self.request.user == self.get_object().master.user


class EventContextMixin(GameContextMixin, FormMixin):
    """
    Mixin class that checks if game events can be sent during a Game
    (e.g. game has been started by the master).
    """

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        flow = GameFlow(self.game)
        if not flow.is_ongoing():
            raise PermissionDenied()
