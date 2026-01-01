import pytest

from game.flows import GameFlow

from .factories import (
    CombatInitativeOrderSetFactory,
    CombatInitiativeRequestFactory,
    CombatInitiativeResponseFactory,
    CombatInitiativeResultFactory,
    GameFactory,
    PlayerFactory,
)


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


@pytest.fixture
def combat_initiative_request(db):
    return CombatInitiativeRequestFactory()


@pytest.fixture
def combat_initiative_response(db):
    return CombatInitiativeResponseFactory()


@pytest.fixture
def combat_initiative_result(db):
    return CombatInitiativeResultFactory()


@pytest.fixture
def combat_initiative_order_set(db):
    return CombatInitativeOrderSetFactory()
