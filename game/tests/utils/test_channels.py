import pytest

from game.schemas import EventType
from game.utils.channels import _get_event_type


@pytest.mark.django_db
class TestGetEventType:
    """Tests for _get_event_type function."""

    def test_combat_initiative_result_returns_correct_type(
        self, combat_initiative_result
    ):
        """Ensure CombatInitiativeResult returns COMBAT_INITIATIVE_RESULT, not COMBAT_INITIATIVE_RESPONSE."""
        event_type = _get_event_type(combat_initiative_result)
        assert event_type == EventType.COMBAT_INITIATIVE_RESULT

    def test_combat_initiative_response_returns_correct_type(
        self, combat_initiative_response
    ):
        """Ensure CombatInitiativeResponse returns COMBAT_INITIATIVE_RESPONSE."""
        event_type = _get_event_type(combat_initiative_response)
        assert event_type == EventType.COMBAT_INITIATIVE_RESPONSE

    def test_combat_initiative_order_set_returns_correct_type(
        self, combat_initiative_order_set
    ):
        """Ensure CombatInitativeOrderSet returns COMBAT_INITIALIZATION_COMPLETE."""
        event_type = _get_event_type(combat_initiative_order_set)
        assert event_type == EventType.COMBAT_INITIALIZATION_COMPLETE

    def test_combat_started_returns_correct_type(self, combat_started):
        """Ensure CombatStarted returns COMBAT_STARTED."""
        event_type = _get_event_type(combat_started)
        assert event_type == EventType.COMBAT_STARTED

    def test_turn_started_returns_correct_type(self, turn_started):
        """Ensure TurnStarted returns TURN_STARTED."""
        event_type = _get_event_type(turn_started)
        assert event_type == EventType.TURN_STARTED

    def test_turn_ended_returns_correct_type(self, turn_ended):
        """Ensure TurnEnded returns TURN_ENDED."""
        event_type = _get_event_type(turn_ended)
        assert event_type == EventType.TURN_ENDED

    def test_round_ended_returns_correct_type(self, round_ended):
        """Ensure RoundEnded returns ROUND_ENDED."""
        event_type = _get_event_type(round_ended)
        assert event_type == EventType.ROUND_ENDED

    def test_combat_ended_returns_correct_type(self, combat_ended):
        """Ensure CombatEnded returns COMBAT_ENDED."""
        event_type = _get_event_type(combat_ended)
        assert event_type == EventType.COMBAT_ENDED
