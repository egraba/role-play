import pytest

from character.tests.factories import (
    CharacterFactory,
    ConditionFactory,
    SpellSettingsFactory,
)
from game.constants.events import RollType
from game.models.events import (
    SpellCast,
    SpellConditionApplied,
    SpellDamageDealt,
    SpellHealingReceived,
    SpellSavingThrow,
)
from game.schemas import EventType
from game.utils.channels import _get_event_type

from ..factories import (
    ActorFactory,
    GameFactory,
    GameStartFactory,
    MessageFactory,
    QuestUpdateFactory,
    RollRequestFactory,
    RollResponseFactory,
    RollResultFactory,
    CombatInitalizationFactory,
)


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

    def test_action_taken_returns_correct_type(self, action_taken):
        """Ensure ActionTaken returns ACTION_TAKEN."""
        event_type = _get_event_type(action_taken)
        assert event_type == EventType.ACTION_TAKEN

    def test_quest_update_returns_correct_type(self):
        """Ensure QuestUpdate returns QUEST_UPDATE."""
        quest_update = QuestUpdateFactory()
        event_type = _get_event_type(quest_update)
        assert event_type == EventType.QUEST_UPDATE

    def test_game_start_returns_correct_type(self):
        """Ensure GameStart returns GAME_START."""
        game_start = GameStartFactory()
        event_type = _get_event_type(game_start)
        assert event_type == EventType.GAME_START

    def test_roll_request_ability_check_returns_correct_type(self):
        """Ensure RollRequest with ABILITY_CHECK returns ABILITY_CHECK_REQUEST."""
        roll_request = RollRequestFactory(roll_type=RollType.ABILITY_CHECK)
        event_type = _get_event_type(roll_request)
        assert event_type == EventType.ABILITY_CHECK_REQUEST

    def test_roll_request_saving_throw_returns_correct_type(self):
        """Ensure RollRequest with SAVING_THROW returns SAVING_THROW_REQUEST."""
        roll_request = RollRequestFactory(roll_type=RollType.SAVING_THROW)
        event_type = _get_event_type(roll_request)
        assert event_type == EventType.SAVING_THROW_REQUEST

    def test_roll_response_ability_check_returns_correct_type(self):
        """Ensure RollResponse with ABILITY_CHECK request returns ABILITY_CHECK_RESPONSE."""
        roll_request = RollRequestFactory(roll_type=RollType.ABILITY_CHECK)
        roll_response = RollResponseFactory(
            request=roll_request, game=roll_request.game
        )
        event_type = _get_event_type(roll_response)
        assert event_type == EventType.ABILITY_CHECK_RESPONSE

    def test_roll_result_ability_check_returns_correct_type(self):
        """Ensure RollResult with ABILITY_CHECK request returns ABILITY_CHECK_RESULT."""
        roll_request = RollRequestFactory(roll_type=RollType.ABILITY_CHECK)
        roll_response = RollResponseFactory(
            request=roll_request, game=roll_request.game
        )
        roll_result = RollResultFactory(
            request=roll_request, response=roll_response, game=roll_request.game
        )
        event_type = _get_event_type(roll_result)
        assert event_type == EventType.ABILITY_CHECK_RESULT

    def test_roll_result_saving_throw_returns_correct_type(self):
        """Ensure RollResult with SAVING_THROW request returns SAVING_THROW_RESULT."""
        roll_request = RollRequestFactory(roll_type=RollType.SAVING_THROW)
        roll_response = RollResponseFactory(
            request=roll_request, game=roll_request.game
        )
        roll_result = RollResultFactory(
            request=roll_request, response=roll_response, game=roll_request.game
        )
        event_type = _get_event_type(roll_result)
        assert event_type == EventType.SAVING_THROW_RESULT

    def test_combat_initialization_returns_correct_type(self):
        """Ensure CombatInitialization returns COMBAT_INITIALIZATION."""
        combat_init = CombatInitalizationFactory()
        event_type = _get_event_type(combat_init)
        assert event_type == EventType.COMBAT_INITIALIZATION

    def test_message_returns_correct_type(self):
        """Ensure Message returns MESSAGE."""
        message = MessageFactory()
        event_type = _get_event_type(message)
        assert event_type == EventType.MESSAGE

    def test_roll_response_saving_throw_returns_correct_type(self):
        """Ensure RollResponse with SAVING_THROW request returns SAVING_THROW_RESPONSE."""
        roll_request = RollRequestFactory(roll_type=RollType.SAVING_THROW)
        roll_response = RollResponseFactory(
            request=roll_request, game=roll_request.game
        )
        event_type = _get_event_type(roll_response)
        assert event_type == EventType.SAVING_THROW_RESPONSE

    def test_spell_cast_returns_correct_type(self):
        """Ensure SpellCast returns SPELL_CAST."""
        game = GameFactory()
        author = ActorFactory()
        caster = CharacterFactory()
        spell = SpellSettingsFactory()
        event = SpellCast.objects.create(
            game=game, author=author, caster=caster, spell=spell, slot_level=1
        )
        event_type = _get_event_type(event)
        assert event_type == EventType.SPELL_CAST

    def test_spell_damage_dealt_returns_correct_type(self):
        """Ensure SpellDamageDealt returns SPELL_DAMAGE_DEALT."""
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory()
        target = CharacterFactory()
        event = SpellDamageDealt.objects.create(
            game=game,
            author=author,
            spell=spell,
            target=target,
            damage=10,
            damage_type="fire",
        )
        event_type = _get_event_type(event)
        assert event_type == EventType.SPELL_DAMAGE_DEALT

    def test_spell_healing_received_returns_correct_type(self):
        """Ensure SpellHealingReceived returns SPELL_HEALING_RECEIVED."""
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory()
        target = CharacterFactory()
        event = SpellHealingReceived.objects.create(
            game=game, author=author, spell=spell, target=target, healing=10
        )
        event_type = _get_event_type(event)
        assert event_type == EventType.SPELL_HEALING_RECEIVED

    def test_spell_condition_applied_returns_correct_type(self):
        """Ensure SpellConditionApplied returns SPELL_CONDITION_APPLIED."""
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory()
        target = CharacterFactory()
        condition = ConditionFactory()
        event = SpellConditionApplied.objects.create(
            game=game, author=author, spell=spell, target=target, condition=condition
        )
        event_type = _get_event_type(event)
        assert event_type == EventType.SPELL_CONDITION_APPLIED

    def test_spell_saving_throw_returns_correct_type(self):
        """Ensure SpellSavingThrow returns SPELL_SAVING_THROW."""
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory()
        target = CharacterFactory()
        event = SpellSavingThrow.objects.create(
            game=game,
            author=author,
            spell=spell,
            target=target,
            save_type="DEX",
            dc=15,
            roll=12,
            success=False,
        )
        event_type = _get_event_type(event)
        assert event_type == EventType.SPELL_SAVING_THROW
