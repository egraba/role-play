import pytest
from datetime import datetime
from pydantic import ValidationError

from game.schemas import EventType, EventOrigin, EventSchema


class TestEventType:
    def test_message_type(self):
        assert EventType.MESSAGE == "message"

    def test_game_start_type(self):
        assert EventType.GAME_START == "game.start"

    def test_combat_event_types(self):
        assert EventType.COMBAT_INITIALIZATION == "combat.initialization"
        assert EventType.COMBAT_INITIATIVE_REQUEST == "combat.initiative.request"
        assert EventType.COMBAT_INITIATIVE_RESPONSE == "combat.initiative.response"
        assert EventType.COMBAT_INITIATIVE_RESULT == "combat.initiative.result"
        assert EventType.COMBAT_STARTED == "combat.started"
        assert EventType.COMBAT_ENDED == "combat.ended"

    def test_turn_event_types(self):
        assert EventType.TURN_STARTED == "turn.started"
        assert EventType.TURN_ENDED == "turn.ended"
        assert EventType.ROUND_ENDED == "round.ended"

    def test_roll_event_types(self):
        assert EventType.ABILITY_CHECK_REQUEST == "ability.check.request"
        assert EventType.ABILITY_CHECK_RESPONSE == "ability.check.response"
        assert EventType.ABILITY_CHECK_RESULT == "ability.check.result"
        assert EventType.SAVING_THROW_REQUEST == "saving.throw.request"
        assert EventType.SAVING_THROW_RESPONSE == "saving.throw.response"
        assert EventType.SAVING_THROW_RESULT == "saving.throw.result"

    def test_spell_event_types(self):
        assert EventType.SPELL_CAST == "spell.cast"
        assert EventType.SPELL_DAMAGE_DEALT == "spell.damage.dealt"
        assert EventType.SPELL_HEALING_RECEIVED == "spell.healing.received"
        assert EventType.SPELL_CONDITION_APPLIED == "spell.condition.applied"
        assert EventType.SPELL_SAVING_THROW == "spell.saving.throw"

    def test_event_type_is_string_enum(self):
        assert isinstance(EventType.MESSAGE.value, str)
        assert str(EventType.MESSAGE) == "message"


class TestEventOrigin:
    def test_client_side_origin(self):
        assert EventOrigin.CLIENT_SIDE.value == 1

    def test_server_side_origin(self):
        assert EventOrigin.SERVER_SIDE.value == 2

    def test_origins_are_distinct(self):
        assert EventOrigin.CLIENT_SIDE != EventOrigin.SERVER_SIDE

    def test_can_combine_flags(self):
        combined = EventOrigin.CLIENT_SIDE | EventOrigin.SERVER_SIDE
        assert EventOrigin.CLIENT_SIDE in combined
        assert EventOrigin.SERVER_SIDE in combined


class TestEventSchema:
    def test_create_minimal_event(self):
        event = EventSchema(
            type=EventType.MESSAGE,
            username="testuser",
            date=datetime(2024, 1, 15, 12, 0, 0),
        )
        assert event.type == EventType.MESSAGE
        assert event.username == "testuser"
        assert event.message is None
        assert event.origin is None

    def test_create_event_with_message(self):
        event = EventSchema(
            type=EventType.MESSAGE,
            username="testuser",
            date=datetime(2024, 1, 15, 12, 0, 0),
            message="Hello, world!",
        )
        assert event.message == "Hello, world!"

    def test_create_event_with_origin(self):
        event = EventSchema(
            type=EventType.MESSAGE,
            username="testuser",
            date=datetime(2024, 1, 15, 12, 0, 0),
            origin=EventOrigin.CLIENT_SIDE,
        )
        assert event.origin == EventOrigin.CLIENT_SIDE

    def test_create_event_with_all_fields(self):
        event = EventSchema(
            type=EventType.GAME_START,
            username="gamemaster",
            date=datetime(2024, 1, 15, 12, 0, 0),
            message="Game is starting!",
            origin=EventOrigin.SERVER_SIDE,
        )
        assert event.type == EventType.GAME_START
        assert event.username == "gamemaster"
        assert event.message == "Game is starting!"
        assert event.origin == EventOrigin.SERVER_SIDE

    def test_missing_required_type_raises_error(self):
        with pytest.raises(ValidationError):
            EventSchema(
                username="testuser",
                date=datetime(2024, 1, 15, 12, 0, 0),
            )

    def test_missing_required_username_raises_error(self):
        with pytest.raises(ValidationError):
            EventSchema(
                type=EventType.MESSAGE,
                date=datetime(2024, 1, 15, 12, 0, 0),
            )

    def test_missing_required_date_raises_error(self):
        with pytest.raises(ValidationError):
            EventSchema(
                type=EventType.MESSAGE,
                username="testuser",
            )

    def test_invalid_type_raises_error(self):
        with pytest.raises(ValidationError):
            EventSchema(
                type="invalid.type",
                username="testuser",
                date=datetime(2024, 1, 15, 12, 0, 0),
            )

    def test_event_serialization_to_dict(self):
        event = EventSchema(
            type=EventType.MESSAGE,
            username="testuser",
            date=datetime(2024, 1, 15, 12, 0, 0),
            message="Test message",
        )
        data = event.model_dump()
        assert data["type"] == EventType.MESSAGE
        assert data["username"] == "testuser"
        assert data["message"] == "Test message"

    def test_all_event_types_can_be_used(self):
        """Ensure all EventType values can be used in EventSchema."""
        for event_type in EventType:
            event = EventSchema(
                type=event_type,
                username="testuser",
                date=datetime(2024, 1, 15, 12, 0, 0),
            )
            assert event.type == event_type
