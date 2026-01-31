import pytest
from django.utils import timezone
from freezegun import freeze_time

from game.constants.events import RollType
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
from game.schemas import EventType
from utils.constants import FREEZED_TIME

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
    FighterFactory,
    GameFactory,
    GameStartFactory,
    MessageFactory,
    PlayerFactory,
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
    @pytest.fixture
    def game_start(self):
        return GameStartFactory()

    def test_creation(self, game_start):
        assert isinstance(game_start, GameStart)

    def test_get_message(self, game_start):
        assert game_start.get_message() == "The game started."


class TestUserInvitationModel:
    @pytest.fixture
    def user_invitation(self):
        return UserInvitationFactory()

    def test_creation(self, user_invitation):
        assert isinstance(user_invitation, UserInvitation)

    def test_get_message(self, user_invitation):
        assert (
            user_invitation.get_message()
            == f"{user_invitation.user} was added to the game."
        )


class TestMessageModel:
    @pytest.fixture
    def message(self):
        return MessageFactory()

    def test_creation(self, message):
        assert isinstance(message, Message)

    @pytest.fixture
    def message_from_master(self):
        game = GameFactory()
        author = ActorFactory()
        author.master = game.master
        return MessageFactory(game=game, author=author)

    def test_get_message_from_master(self, message_from_master):
        assert (
            message_from_master.get_message()
            == f"The Master said: {message_from_master.content}"
        )

    @pytest.fixture
    def message_from_player(self):
        game = GameFactory()
        author = ActorFactory()
        player = PlayerFactory(game=game)
        author.player = player
        return MessageFactory(game=game, author=author)

    def test_get_message_from_player(self, message_from_player):
        assert (
            message_from_player.get_message()
            == f"{message_from_player.author} said: {message_from_player.content}"
        )


class TestQuestUpdateModel:
    @pytest.fixture
    def quest_update(self):
        return QuestUpdateFactory()

    def test_creation(self, quest_update):
        assert isinstance(quest_update, QuestUpdate)

    def test_str(self, quest_update):
        assert str(quest_update) == quest_update.quest.environment[:10]

    def test_get_message(self, quest_update):
        assert quest_update.get_message() == "The Master updated the quest."


class TestRollRequestModel:
    @pytest.fixture
    def roll_request(self):
        return RollRequestFactory()

    def test_creation(self, roll_request):
        assert isinstance(roll_request, RollRequest)

    def test_get_message(self, roll_request):
        assert (
            roll_request.get_message()
            == f"{roll_request.player} needs to perform a {roll_request.ability_type} check! \
            Difficulty: {roll_request.get_difficulty_class_display()}."
        )


class TestRollResponseModel:
    @pytest.fixture
    def roll_response(self):
        return RollResponseFactory(request=RollRequestFactory())

    def test_creation(self, roll_response):
        assert isinstance(roll_response, RollResponse)

    def test_get_message(self, roll_response):
        assert (
            roll_response.get_message()
            == f"{roll_response.request.player} performed an ability check!"
        )


class TestRollResultModel:
    @pytest.fixture
    def roll_result(self):
        roll_request = RollRequestFactory()
        roll_response = RollResponseFactory(request=roll_request)
        return RollResultFactory(request=roll_request, response=roll_response)

    def test_creation(self, roll_result):
        assert isinstance(roll_result, RollResult)

    def test_get_message(self, roll_result):
        assert (
            roll_result.get_message()
            == f"{roll_result.request.player}'s score: {roll_result.score}, \
            {roll_result.request.get_roll_type_display()} result: {roll_result.get_result_display()}"
        )


class TestCombatInitializationModel:
    @pytest.fixture
    def combat_init(self):
        return CombatInitalizationFactory()

    def test_creation(self, combat_init):
        assert isinstance(combat_init, CombatInitialization)

    def test_get_message(self, combat_init):
        assert combat_init.get_message().startswith("Combat!")

    def test_get_message_single_fighter_no_initiative_order_prefix(self, combat_init):
        # Remove all fighters and add just one
        combat_init.combat.fighter_set.all().delete()
        FighterFactory(combat=combat_init.combat, dexterity_check=10)
        message = combat_init.get_message()
        assert message.startswith("Combat!")
        assert "Initiative order:" not in message

    def test_get_message_multiple_fighters_has_initiative_order_prefix(
        self, combat_init
    ):
        # Ensure there are at least 2 fighters
        combat_init.combat.fighter_set.all().delete()
        FighterFactory(combat=combat_init.combat, dexterity_check=10)
        FighterFactory(combat=combat_init.combat, dexterity_check=15)
        message = combat_init.get_message()
        assert message.startswith("Combat! Initiative order:")


class TestCombatStartedModel:
    @pytest.fixture
    def combat_started(self):
        return CombatStartedFactory()

    def test_creation(self, combat_started):
        assert isinstance(combat_started, CombatStarted)

    def test_get_message(self, combat_started):
        assert (
            combat_started.get_message()
            == "Combat has begun! Roll for initiative order has been determined."
        )


class TestTurnStartedModel:
    @pytest.fixture
    def turn_started(self):
        return TurnStartedFactory()

    def test_creation(self, turn_started):
        assert isinstance(turn_started, TurnStarted)

    def test_get_message(self, turn_started):
        expected = f"Round {turn_started.round_number}: {turn_started.fighter.character.name}'s turn!"
        assert turn_started.get_message() == expected


class TestTurnEndedModel:
    @pytest.fixture
    def turn_ended(self):
        return TurnEndedFactory()

    def test_creation(self, turn_ended):
        assert isinstance(turn_ended, TurnEnded)

    def test_get_message(self, turn_ended):
        expected = f"{turn_ended.fighter.character.name}'s turn has ended."
        assert turn_ended.get_message() == expected


class TestRoundEndedModel:
    @pytest.fixture
    def round_ended(self):
        return RoundEndedFactory()

    def test_creation(self, round_ended):
        assert isinstance(round_ended, RoundEnded)

    def test_get_message(self, round_ended):
        expected = f"Round {round_ended.round_number} has ended."
        assert round_ended.get_message() == expected


class TestCombatEndedModel:
    @pytest.fixture
    def combat_ended(self):
        return CombatEndedFactory()

    def test_creation(self, combat_ended):
        assert isinstance(combat_ended, CombatEnded)

    def test_get_message(self, combat_ended):
        assert combat_ended.get_message() == "Combat has ended."


class TestSpellCastModel:
    @pytest.fixture
    def spell_cast(self):
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
        return event

    def test_creation(self, spell_cast):
        assert isinstance(spell_cast, SpellCast)
        assert spell_cast.caster.name == "Gandalf"
        assert spell_cast.spell.name == "Fireball"
        assert spell_cast.slot_level == 3

    def test_get_message_no_targets(self, spell_cast):
        message = spell_cast.get_message()
        assert "Gandalf cast Fireball" in message

    def test_get_message_with_targets(self, spell_cast):
        target1 = CharacterFactory(name="Goblin")
        target2 = CharacterFactory(name="Orc")
        spell_cast.targets.add(target1, target2)

        message = spell_cast.get_message()
        assert "Gandalf cast Fireball on" in message
        assert "Goblin" in message
        assert "Orc" in message


class TestSpellDamageDealtModel:
    @pytest.fixture
    def spell_damage(self):
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory(name="Fireball")
        target = CharacterFactory(name="Goblin")
        return SpellDamageDealt.objects.create(
            game=game,
            author=author,
            spell=spell,
            target=target,
            damage=28,
            damage_type="fire",
        )

    def test_creation(self, spell_damage):
        assert isinstance(spell_damage, SpellDamageDealt)
        assert spell_damage.damage == 28
        assert spell_damage.damage_type == "fire"

    def test_get_message(self, spell_damage):
        message = spell_damage.get_message()
        assert "Goblin took 28 fire damage from Fireball" in message


class TestSpellHealingReceivedModel:
    @pytest.fixture
    def spell_healing(self):
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory(name="Cure Wounds")
        target = CharacterFactory(name="Fighter")
        return SpellHealingReceived.objects.create(
            game=game,
            author=author,
            spell=spell,
            target=target,
            healing=12,
        )

    def test_creation(self, spell_healing):
        assert isinstance(spell_healing, SpellHealingReceived)
        assert spell_healing.healing == 12

    def test_get_message(self, spell_healing):
        message = spell_healing.get_message()
        assert "Fighter was healed for 12 HP by Cure Wounds" in message


class TestSpellConditionAppliedModel:
    @pytest.fixture
    def spell_condition(self):
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory(name="Hold Person")
        target = CharacterFactory(name="Bandit")
        condition = ConditionFactory(name="paralyzed")
        return SpellConditionApplied.objects.create(
            game=game,
            author=author,
            spell=spell,
            target=target,
            condition=condition,
        )

    def test_creation(self, spell_condition):
        assert isinstance(spell_condition, SpellConditionApplied)
        assert spell_condition.condition.name == "paralyzed"

    def test_get_message(self, spell_condition):
        message = spell_condition.get_message()
        assert "Bandit is now" in message
        assert "Hold Person" in message


class TestSpellSavingThrowModel:
    @pytest.fixture
    def spell_save_success(self):
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory(name="Fireball")
        target = CharacterFactory(name="Rogue")
        return SpellSavingThrow.objects.create(
            game=game,
            author=author,
            spell=spell,
            target=target,
            save_type="DEX",
            dc=15,
            roll=18,
            success=True,
        )

    @pytest.fixture
    def spell_save_failure(self):
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory(name="Hold Person")
        target = CharacterFactory(name="Warrior")
        return SpellSavingThrow.objects.create(
            game=game,
            author=author,
            spell=spell,
            target=target,
            save_type="WIS",
            dc=14,
            roll=10,
            success=False,
        )

    def test_creation_success(self, spell_save_success):
        assert isinstance(spell_save_success, SpellSavingThrow)
        assert spell_save_success.success is True
        assert spell_save_success.save_type == "DEX"
        assert spell_save_success.dc == 15
        assert spell_save_success.roll == 18

    def test_creation_failure(self, spell_save_failure):
        assert isinstance(spell_save_failure, SpellSavingThrow)
        assert spell_save_failure.success is False

    def test_get_message_success(self, spell_save_success):
        message = spell_save_success.get_message()
        assert "Rogue succeeded" in message
        assert "DEX save" in message
        assert "DC 15" in message
        assert "Fireball" in message
        assert "18" in message

    def test_get_message_failure(self, spell_save_failure):
        message = spell_save_failure.get_message()
        assert "Warrior failed" in message
        assert "WIS save" in message
        assert "DC 14" in message
        assert "Hold Person" in message
        assert "10" in message


class TestGetEventType:
    """Tests for get_event_type() method on all Event subclasses."""

    def test_game_start_event_type(self):
        event = GameStartFactory()
        assert event.get_event_type() == EventType.GAME_START

    def test_message_event_type(self):
        event = MessageFactory()
        assert event.get_event_type() == EventType.MESSAGE

    def test_quest_update_event_type(self):
        event = QuestUpdateFactory()
        assert event.get_event_type() == EventType.QUEST_UPDATE

    def test_roll_request_ability_check_event_type(self):
        event = RollRequestFactory(roll_type=RollType.ABILITY_CHECK)
        assert event.get_event_type() == EventType.ABILITY_CHECK_REQUEST

    def test_roll_request_saving_throw_event_type(self):
        event = RollRequestFactory(roll_type=RollType.SAVING_THROW)
        assert event.get_event_type() == EventType.SAVING_THROW_REQUEST

    def test_roll_response_ability_check_event_type(self):
        request = RollRequestFactory(roll_type=RollType.ABILITY_CHECK)
        event = RollResponseFactory(request=request, game=request.game)
        assert event.get_event_type() == EventType.ABILITY_CHECK_RESPONSE

    def test_roll_response_saving_throw_event_type(self):
        request = RollRequestFactory(roll_type=RollType.SAVING_THROW)
        event = RollResponseFactory(request=request, game=request.game)
        assert event.get_event_type() == EventType.SAVING_THROW_RESPONSE

    def test_roll_result_ability_check_event_type(self):
        request = RollRequestFactory(roll_type=RollType.ABILITY_CHECK)
        response = RollResponseFactory(request=request, game=request.game)
        event = RollResultFactory(request=request, response=response, game=request.game)
        assert event.get_event_type() == EventType.ABILITY_CHECK_RESULT

    def test_roll_result_saving_throw_event_type(self):
        request = RollRequestFactory(roll_type=RollType.SAVING_THROW)
        response = RollResponseFactory(request=request, game=request.game)
        event = RollResultFactory(request=request, response=response, game=request.game)
        assert event.get_event_type() == EventType.SAVING_THROW_RESULT

    def test_combat_initialization_event_type(self):
        event = CombatInitalizationFactory()
        assert event.get_event_type() == EventType.COMBAT_INITIALIZATION

    def test_combat_initiative_request_event_type(self):
        event = CombatInitiativeRequestFactory()
        assert event.get_event_type() == EventType.COMBAT_INITIATIVE_REQUEST

    def test_combat_initiative_response_event_type(self):
        event = CombatInitiativeResponseFactory()
        assert event.get_event_type() == EventType.COMBAT_INITIATIVE_RESPONSE

    def test_combat_initiative_result_event_type(self):
        request = CombatInitiativeRequestFactory()
        response = CombatInitiativeResponseFactory(request=request)
        event = CombatInitiativeResultFactory(
            request=request, response=response, fighter=request.fighter
        )
        assert event.get_event_type() == EventType.COMBAT_INITIATIVE_RESULT

    def test_combat_initiative_order_set_event_type(self):
        event = CombatInitativeOrderSetFactory()
        assert event.get_event_type() == EventType.COMBAT_INITIALIZATION_COMPLETE

    def test_combat_started_event_type(self):
        event = CombatStartedFactory()
        assert event.get_event_type() == EventType.COMBAT_STARTED

    def test_turn_started_event_type(self):
        event = TurnStartedFactory()
        assert event.get_event_type() == EventType.TURN_STARTED

    def test_turn_ended_event_type(self):
        event = TurnEndedFactory()
        assert event.get_event_type() == EventType.TURN_ENDED

    def test_round_ended_event_type(self):
        event = RoundEndedFactory()
        assert event.get_event_type() == EventType.ROUND_ENDED

    def test_combat_ended_event_type(self):
        event = CombatEndedFactory()
        assert event.get_event_type() == EventType.COMBAT_ENDED

    def test_action_taken_event_type(self):
        event = ActionTakenFactory()
        assert event.get_event_type() == EventType.ACTION_TAKEN

    def test_spell_cast_event_type(self):
        game = GameFactory()
        author = ActorFactory()
        caster = CharacterFactory()
        spell = SpellSettingsFactory()
        event = SpellCast.objects.create(
            game=game, author=author, caster=caster, spell=spell, slot_level=1
        )
        assert event.get_event_type() == EventType.SPELL_CAST

    def test_spell_damage_dealt_event_type(self):
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
        assert event.get_event_type() == EventType.SPELL_DAMAGE_DEALT

    def test_spell_healing_received_event_type(self):
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory()
        target = CharacterFactory()
        event = SpellHealingReceived.objects.create(
            game=game, author=author, spell=spell, target=target, healing=10
        )
        assert event.get_event_type() == EventType.SPELL_HEALING_RECEIVED

    def test_spell_condition_applied_event_type(self):
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory()
        target = CharacterFactory()
        condition = ConditionFactory()
        event = SpellConditionApplied.objects.create(
            game=game, author=author, spell=spell, target=target, condition=condition
        )
        assert event.get_event_type() == EventType.SPELL_CONDITION_APPLIED

    def test_spell_saving_throw_event_type(self):
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
        assert event.get_event_type() == EventType.SPELL_SAVING_THROW

    def test_base_event_get_event_type_raises(self):
        """Test that base Event class raises NotImplementedError."""
        event = EventFactory()
        with pytest.raises(NotImplementedError):
            event.get_event_type()

    def test_dice_roll_event_type(self):
        """Test DiceRoll event type."""
        event = DiceRollFactory()
        assert event.get_event_type() == EventType.DICE_ROLL


class TestDiceRollModel:
    """Tests for DiceRoll model."""

    @pytest.fixture
    def dice_roll(self):
        return DiceRollFactory()

    def test_creation(self, dice_roll):
        assert isinstance(dice_roll, DiceRoll)
        assert dice_roll.dice_notation == "2d6"
        assert dice_roll.dice_type == 6
        assert dice_roll.num_dice == 2
        assert dice_roll.individual_rolls == [3, 4]
        assert dice_roll.total == 7

    def test_get_message_basic(self, dice_roll):
        message = dice_roll.get_message()
        assert "2d6" in message
        assert "[3, 4]" in message
        assert "7" in message

    def test_get_message_with_positive_modifier(self):
        dice_roll = DiceRollFactory(
            dice_notation="1d20",
            dice_type=20,
            num_dice=1,
            modifier=5,
            individual_rolls=[15],
            total=20,
        )
        message = dice_roll.get_message()
        assert "+5" in message
        assert "20" in message

    def test_get_message_with_negative_modifier(self):
        dice_roll = DiceRollFactory(
            dice_notation="1d20",
            dice_type=20,
            num_dice=1,
            modifier=-2,
            individual_rolls=[10],
            total=8,
        )
        message = dice_roll.get_message()
        assert "-2" in message
        assert "8" in message

    def test_get_message_with_purpose(self):
        dice_roll = DiceRollFactory(
            roll_purpose="Perception check",
        )
        message = dice_roll.get_message()
        assert "for Perception check" in message

    def test_get_message_from_master(self):
        game = GameFactory()
        author = ActorFactory()
        author.master = game.master
        dice_roll = DiceRollFactory(game=game, author=author)
        message = dice_roll.get_message()
        assert "The Master" in message

    def test_get_message_from_player(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        dice_roll = DiceRollFactory(game=game, author=player)
        message = dice_roll.get_message()
        assert str(player) in message
