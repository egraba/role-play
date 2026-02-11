import pytest

from game.constants.event_registry import get_event_type
from game.constants.events import RollType
from game.models.events import (
    SpellCast,
    SpellConditionApplied,
    SpellDamageDealt,
    SpellHealingReceived,
    SpellSavingThrow,
)
from game.schemas import EventType

from character.tests.factories import (
    CharacterFactory,
    ConditionFactory,
    SpellSettingsFactory,
)

from ..factories import (
    ActionTakenFactory,
    ActorFactory,
    CombatEndedFactory,
    CombatInitalizationFactory,
    CombatInitativeOrderSetFactory,
    CombatInitiativeRequestFactory,
    CombatInitiativeResponseFactory,
    CombatInitiativeResultFactory,
    CombatStartedFactory,
    DiceRollFactory,
    EventFactory,
    GameFactory,
    GameStartFactory,
    MessageFactory,
    QuestUpdateFactory,
    RollRequestFactory,
    RollResponseFactory,
    RollResultFactory,
    RoundEndedFactory,
    TurnEndedFactory,
    TurnStartedFactory,
    UserInvitationFactory,
)

pytestmark = pytest.mark.django_db


class TestGetEventType:
    """Tests for get_event_type() registry function."""

    def test_game_start(self):
        assert get_event_type(GameStartFactory()) == EventType.GAME_START

    def test_message(self):
        assert get_event_type(MessageFactory()) == EventType.MESSAGE

    def test_user_invitation(self):
        assert get_event_type(UserInvitationFactory()) == EventType.MESSAGE

    def test_quest_update(self):
        assert get_event_type(QuestUpdateFactory()) == EventType.QUEST_UPDATE

    def test_roll_request_ability_check(self):
        event = RollRequestFactory(roll_type=RollType.ABILITY_CHECK)
        assert get_event_type(event) == EventType.ABILITY_CHECK_REQUEST

    def test_roll_request_saving_throw(self):
        event = RollRequestFactory(roll_type=RollType.SAVING_THROW)
        assert get_event_type(event) == EventType.SAVING_THROW_REQUEST

    def test_roll_response_ability_check(self):
        request = RollRequestFactory(roll_type=RollType.ABILITY_CHECK)
        event = RollResponseFactory(request=request, game=request.game)
        assert get_event_type(event) == EventType.ABILITY_CHECK_RESPONSE

    def test_roll_response_saving_throw(self):
        request = RollRequestFactory(roll_type=RollType.SAVING_THROW)
        event = RollResponseFactory(request=request, game=request.game)
        assert get_event_type(event) == EventType.SAVING_THROW_RESPONSE

    def test_roll_result_ability_check(self):
        request = RollRequestFactory(roll_type=RollType.ABILITY_CHECK)
        response = RollResponseFactory(request=request, game=request.game)
        event = RollResultFactory(request=request, response=response, game=request.game)
        assert get_event_type(event) == EventType.ABILITY_CHECK_RESULT

    def test_roll_result_saving_throw(self):
        request = RollRequestFactory(roll_type=RollType.SAVING_THROW)
        response = RollResponseFactory(request=request, game=request.game)
        event = RollResultFactory(request=request, response=response, game=request.game)
        assert get_event_type(event) == EventType.SAVING_THROW_RESULT

    def test_combat_initialization(self):
        assert (
            get_event_type(CombatInitalizationFactory())
            == EventType.COMBAT_INITIALIZATION
        )

    def test_combat_initiative_request(self):
        assert (
            get_event_type(CombatInitiativeRequestFactory())
            == EventType.COMBAT_INITIATIVE_REQUEST
        )

    def test_combat_initiative_response(self):
        assert (
            get_event_type(CombatInitiativeResponseFactory())
            == EventType.COMBAT_INITIATIVE_RESPONSE
        )

    def test_combat_initiative_result(self):
        request = CombatInitiativeRequestFactory()
        response = CombatInitiativeResponseFactory(request=request)
        event = CombatInitiativeResultFactory(
            request=request, response=response, fighter=request.fighter
        )
        assert get_event_type(event) == EventType.COMBAT_INITIATIVE_RESULT

    def test_combat_initiative_order_set(self):
        assert (
            get_event_type(CombatInitativeOrderSetFactory())
            == EventType.COMBAT_INITIALIZATION_COMPLETE
        )

    def test_combat_started(self):
        assert get_event_type(CombatStartedFactory()) == EventType.COMBAT_STARTED

    def test_turn_started(self):
        assert get_event_type(TurnStartedFactory()) == EventType.TURN_STARTED

    def test_turn_ended(self):
        assert get_event_type(TurnEndedFactory()) == EventType.TURN_ENDED

    def test_round_ended(self):
        assert get_event_type(RoundEndedFactory()) == EventType.ROUND_ENDED

    def test_combat_ended(self):
        assert get_event_type(CombatEndedFactory()) == EventType.COMBAT_ENDED

    def test_action_taken(self):
        assert get_event_type(ActionTakenFactory()) == EventType.ACTION_TAKEN

    def test_spell_cast(self):
        game = GameFactory()
        author = ActorFactory()
        caster = CharacterFactory()
        spell = SpellSettingsFactory()
        event = SpellCast.objects.create(
            game=game, author=author, caster=caster, spell=spell, slot_level=1
        )
        assert get_event_type(event) == EventType.SPELL_CAST

    def test_spell_damage_dealt(self):
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
        assert get_event_type(event) == EventType.SPELL_DAMAGE_DEALT

    def test_spell_healing_received(self):
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory()
        target = CharacterFactory()
        event = SpellHealingReceived.objects.create(
            game=game, author=author, spell=spell, target=target, healing=10
        )
        assert get_event_type(event) == EventType.SPELL_HEALING_RECEIVED

    def test_spell_condition_applied(self):
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory()
        target = CharacterFactory()
        condition = ConditionFactory()
        event = SpellConditionApplied.objects.create(
            game=game, author=author, spell=spell, target=target, condition=condition
        )
        assert get_event_type(event) == EventType.SPELL_CONDITION_APPLIED

    def test_spell_saving_throw(self):
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
        assert get_event_type(event) == EventType.SPELL_SAVING_THROW

    def test_dice_roll(self):
        assert get_event_type(DiceRollFactory()) == EventType.DICE_ROLL

    def test_base_event_raises(self):
        event = EventFactory()
        with pytest.raises(NotImplementedError):
            get_event_type(event)
