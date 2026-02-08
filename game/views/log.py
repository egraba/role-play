from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from character.models.character import Character

from ..models.events import Event
from ..models.game import Game
from ..serializers import serialize_game_log_event


class GameLogView(LoginRequiredMixin, View):
    """API endpoint to fetch recent game log events."""

    def get(self, request, game_id: int) -> JsonResponse:
        game = Game.objects.get(id=game_id)

        # Get last 50 events, oldest first
        events = (
            Event.objects.filter(game=game).select_subclasses().order_by("-date")[:50]
        )
        events = list(reversed(events))

        serialized_events = [serialize_game_log_event(e) for e in events]

        # Get characters in game for filter dropdown
        characters = list(
            Character.objects.filter(player__game=game).values("id", "name")
        )

        return JsonResponse(
            {
                "events": serialized_events,
                "characters": characters,
            }
        )
