import pytest
from django.core.cache import cache

from game.flows import GameFlow
from game.utils.cache import game_key

from .factories import GameFactory, PlayerFactory


@pytest.mark.django_db
def test_game_states():
    game = GameFactory()
    flow = GameFlow(game)

    # Under preparation
    assert flow.is_under_preparation()
    assert flow.is_ongoing() is False

    # Ongoing
    number_of_players = 5
    for _ in range(number_of_players):
        PlayerFactory(game=game)
    flow.start()
    assert flow.is_under_preparation() is False
    assert flow.is_ongoing()


@pytest.mark.django_db
def test_game_state_transition_invalidates_cache():
    """Test that the game cache is invalidated when the state transitions."""
    game = GameFactory()

    # Simulate the game being cached
    cache.set(game_key(game.id), game)
    assert cache.get(game_key(game.id)) is not None

    # Add players and start the game
    for _ in range(2):
        PlayerFactory(game=game)

    flow = GameFlow(game)
    flow.start()

    # Cache should be invalidated after state transition
    assert cache.get(game_key(game.id)) is None
