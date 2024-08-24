from django.utils import timezone
from viewflow import fsm

from .constants.game import GameState


class GameFlow:
    state = fsm.State(GameState, default=GameState.UNDER_PREPARATION)

    def __init__(self, game):
        self.game = game

    @state.setter()
    def _set_game_state(self, value):
        self.game.state = value

    @state.getter()
    def _get_game_state(self):
        return self.game.state

    @state.on_success()
    def _on_transition_success(self, descriptor, source, target):
        self.game.save()

    def can_start(self):
        return self.game.player_set.count() >= 2

    @state.transition(
        source=GameState.UNDER_PREPARATION,
        target=GameState.ONGOING,
        conditions=[can_start],
    )
    def start(self):
        self.game.start_date = timezone.now()
        self.game.save()

    def is_under_preparation(self):
        return self.game.state == GameState.UNDER_PREPARATION

    def is_ongoing(self):
        return self.game.state == GameState.ONGOING
