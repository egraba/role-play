import pytest
from django.utils import timezone
from freezegun import freeze_time

from game.models.events import (
    CombatEnded,
    CombatInitialization,
    CombatStarted,
    DiceRoll,
    Event,
    GameStart,
    Message,
    QuestUpdate,
    RollRequest,
    RollResponse,
    RollResult,
    RoundEnded,
    SpellCast,
    SpellConditionApplied,
    SpellDamageDealt,
    SpellHealingReceived,
    SpellSavingThrow,
    TurnEnded,
    TurnStarted,
    UserInvitation,
)
from utils.constants import FREEZED_TIME

from character.tests.factories import (
    CharacterFactory,
    ConditionFactory,
    SpellSettingsFactory,
)

from ..factories import (
    ActorFactory,
    CombatEndedFactory,
    CombatInitalizationFactory,
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


class TestEventModel:
    @freeze_time(FREEZED_TIME)
    def test_creation(self):
        event = EventFactory()
        assert isinstance(event, Event)
        assert event.date == timezone.now()


class TestGameStartModel:
    def test_creation(self):
        game_start = GameStartFactory()
        assert isinstance(game_start, GameStart)


class TestUserInvitationModel:
    def test_creation(self):
        user_invitation = UserInvitationFactory()
        assert isinstance(user_invitation, UserInvitation)


class TestMessageModel:
    def test_creation(self):
        message = MessageFactory()
        assert isinstance(message, Message)

    def test_str(self):
        message = MessageFactory()
        assert str(message) == message.content


class TestQuestUpdateModel:
    def test_creation(self):
        quest_update = QuestUpdateFactory()
        assert isinstance(quest_update, QuestUpdate)

    def test_str(self):
        quest_update = QuestUpdateFactory()
        assert str(quest_update) == quest_update.quest.environment[:10]


class TestRollRequestModel:
    def test_creation(self):
        roll_request = RollRequestFactory()
        assert isinstance(roll_request, RollRequest)


class TestRollResponseModel:
    def test_creation(self):
        roll_response = RollResponseFactory(request=RollRequestFactory())
        assert isinstance(roll_response, RollResponse)


class TestRollResultModel:
    def test_creation(self):
        roll_request = RollRequestFactory()
        roll_response = RollResponseFactory(request=roll_request)
        roll_result = RollResultFactory(request=roll_request, response=roll_response)
        assert isinstance(roll_result, RollResult)


class TestCombatInitializationModel:
    def test_creation(self):
        combat_init = CombatInitalizationFactory()
        assert isinstance(combat_init, CombatInitialization)


class TestCombatStartedModel:
    def test_creation(self):
        combat_started = CombatStartedFactory()
        assert isinstance(combat_started, CombatStarted)


class TestTurnStartedModel:
    def test_creation(self):
        turn_started = TurnStartedFactory()
        assert isinstance(turn_started, TurnStarted)


class TestTurnEndedModel:
    def test_creation(self):
        turn_ended = TurnEndedFactory()
        assert isinstance(turn_ended, TurnEnded)


class TestRoundEndedModel:
    def test_creation(self):
        round_ended = RoundEndedFactory()
        assert isinstance(round_ended, RoundEnded)


class TestCombatEndedModel:
    def test_creation(self):
        combat_ended = CombatEndedFactory()
        assert isinstance(combat_ended, CombatEnded)


class TestSpellCastModel:
    def test_creation(self):
        game = GameFactory()
        author = ActorFactory()
        caster = CharacterFactory(name="Gandalf")
        spell = SpellSettingsFactory(name="Fireball")
        event = SpellCast.objects.create(
            game=game,
            author=author,
            caster=caster,
            spell=spell,
            slot_level=3,
        )
        assert isinstance(event, SpellCast)
        assert event.caster.name == "Gandalf"
        assert event.spell.name == "Fireball"
        assert event.slot_level == 3


class TestSpellDamageDealtModel:
    def test_creation(self):
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory(name="Fireball")
        target = CharacterFactory(name="Goblin")
        event = SpellDamageDealt.objects.create(
            game=game,
            author=author,
            spell=spell,
            target=target,
            damage=28,
            damage_type="fire",
        )
        assert isinstance(event, SpellDamageDealt)
        assert event.damage == 28
        assert event.damage_type == "fire"


class TestSpellHealingReceivedModel:
    def test_creation(self):
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory(name="Cure Wounds")
        target = CharacterFactory(name="Fighter")
        event = SpellHealingReceived.objects.create(
            game=game,
            author=author,
            spell=spell,
            target=target,
            healing=12,
        )
        assert isinstance(event, SpellHealingReceived)
        assert event.healing == 12


class TestSpellConditionAppliedModel:
    def test_creation(self):
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory(name="Hold Person")
        target = CharacterFactory(name="Bandit")
        condition = ConditionFactory(name="paralyzed")
        event = SpellConditionApplied.objects.create(
            game=game,
            author=author,
            spell=spell,
            target=target,
            condition=condition,
        )
        assert isinstance(event, SpellConditionApplied)
        assert event.condition.name == "paralyzed"


class TestSpellSavingThrowModel:
    def test_creation_success(self):
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory(name="Fireball")
        target = CharacterFactory(name="Rogue")
        event = SpellSavingThrow.objects.create(
            game=game,
            author=author,
            spell=spell,
            target=target,
            save_type="DEX",
            dc=15,
            roll=18,
            success=True,
        )
        assert isinstance(event, SpellSavingThrow)
        assert event.success is True
        assert event.save_type == "DEX"
        assert event.dc == 15
        assert event.roll == 18

    def test_creation_failure(self):
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory(name="Hold Person")
        target = CharacterFactory(name="Warrior")
        event = SpellSavingThrow.objects.create(
            game=game,
            author=author,
            spell=spell,
            target=target,
            save_type="WIS",
            dc=14,
            roll=10,
            success=False,
        )
        assert isinstance(event, SpellSavingThrow)
        assert event.success is False


class TestDiceRollModel:
    def test_creation(self):
        dice_roll = DiceRollFactory()
        assert isinstance(dice_roll, DiceRoll)
        assert dice_roll.dice_notation == "2d6"
        assert dice_roll.dice_type == 6
        assert dice_roll.num_dice == 2
        assert dice_roll.individual_rolls == [3, 4]
        assert dice_roll.total == 7
