import pytest

from game.flows import GameFlow

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
