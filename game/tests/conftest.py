import pytest

from game.flows import GameFlow

from .factories import (
    ActionTakenFactory,
    CombatEndedFactory,
    CombatInitativeOrderSetFactory,
    CombatInitiativeRequestFactory,
    CombatInitiativeResponseFactory,
    CombatInitiativeResultFactory,
    CombatStartedFactory,
    GameFactory,
    PlayerFactory,
    RoundEndedFactory,
    TurnEndedFactory,
    TurnStartedFactory,
)


@pytest.fixture
def started_game(db):
    """Create a started game with players.

    Note: This fixture is function-scoped to avoid race conditions
    with parallel test execution (pytest-xdist).
    """
    game = GameFactory()
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


@pytest.fixture
def combat_started(db):
    return CombatStartedFactory()


@pytest.fixture
def turn_started(db):
    return TurnStartedFactory()


@pytest.fixture
def turn_ended(db):
    return TurnEndedFactory()


@pytest.fixture
def round_ended(db):
    return RoundEndedFactory()


@pytest.fixture
def combat_ended(db):
    return CombatEndedFactory()


@pytest.fixture
def action_taken(db):
    return ActionTakenFactory()
