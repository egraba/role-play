import pytest
import freezegun

from game.flows import GameFlow

from .factories import GameFactory, PlayerFactory

freezegun.configure(extend_ignore_list=["celery"])


@pytest.fixture(scope="session")
def started_game(django_db_blocker):
    with django_db_blocker.unblock():
        game = GameFactory(master__user__username="master")
        number_of_players = 3
        for _ in range(number_of_players):
            PlayerFactory(game=game)
        flow = GameFlow(game)
        flow.start()
        return game
