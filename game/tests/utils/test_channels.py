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
