import pytest

from game.presenters import format_event_message
from game.models.events import (
    SpellCast,
    SpellConditionApplied,
    SpellDamageDealt,
    SpellHealingReceived,
    SpellSavingThrow,
)

from character.tests.factories import (
    CharacterFactory,
    ConditionFactory,
    SpellSettingsFactory,
)

from .factories import (
    ActorFactory,
    CombatInitalizationFactory,
    CombatStartedFactory,
    DiceRollFactory,
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


class TestFormatGameStart:
    def test_message(self):
        event = GameStartFactory()
        assert format_event_message(event) == "The game started."


class TestFormatUserInvitation:
    def test_message(self):
        event = UserInvitationFactory()
        assert format_event_message(event) == f"{event.user} was added to the game."


class TestFormatMessage:
    def test_from_master(self):
        game = GameFactory()
        author = ActorFactory()
        author.master = game.master
        event = MessageFactory(game=game, author=author)
        assert format_event_message(event) == f"The Master said: {event.content}"

    def test_from_player(self):
        game = GameFactory()
        author = ActorFactory()
        player = PlayerFactory(game=game)
        author.player = player
        event = MessageFactory(game=game, author=author)
        assert format_event_message(event) == f"{event.author} said: {event.content}"


class TestFormatQuestUpdate:
    def test_message(self):
        event = QuestUpdateFactory()
        assert format_event_message(event) == "The Master updated the quest."


class TestFormatRollRequest:
    def test_message(self):
        event = RollRequestFactory()
        expected = f"{event.player} needs to perform a {event.ability_type} check! \
            Difficulty: {event.get_difficulty_class_display()}."
        assert format_event_message(event) == expected


class TestFormatRollResponse:
    def test_message(self):
        request = RollRequestFactory()
        event = RollResponseFactory(request=request)
        assert (
            format_event_message(event)
            == f"{event.request.player} performed an ability check!"
        )


class TestFormatRollResult:
    def test_message(self):
        request = RollRequestFactory()
        response = RollResponseFactory(request=request)
        event = RollResultFactory(request=request, response=response)
        expected = f"{event.request.player}'s score: {event.score}, \
            {event.request.get_roll_type_display()} result: {event.get_result_display()}"
        assert format_event_message(event) == expected


class TestFormatCombatInitialization:
    def test_message_starts_with_combat(self):
        event = CombatInitalizationFactory()
        assert format_event_message(event).startswith("Combat!")

    def test_single_fighter_no_initiative_order_prefix(self):
        event = CombatInitalizationFactory()
        event.combat.fighter_set.all().delete()
        FighterFactory(combat=event.combat, dexterity_check=10)
        message = format_event_message(event)
        assert message.startswith("Combat!")
        assert "Initiative order:" not in message

    def test_multiple_fighters_has_initiative_order_prefix(self):
        event = CombatInitalizationFactory()
        event.combat.fighter_set.all().delete()
        FighterFactory(combat=event.combat, dexterity_check=10)
        FighterFactory(combat=event.combat, dexterity_check=15)
        message = format_event_message(event)
        assert message.startswith("Combat! Initiative order:")


class TestFormatCombatStarted:
    def test_message(self):
        event = CombatStartedFactory()
        assert (
            format_event_message(event)
            == "Combat has begun! Roll for initiative order has been determined."
        )


class TestFormatTurnStarted:
    def test_message(self):
        event = TurnStartedFactory()
        expected = f"Round {event.round_number}: {event.fighter.character.name}'s turn!"
        assert format_event_message(event) == expected


class TestFormatTurnEnded:
    def test_message(self):
        event = TurnEndedFactory()
        expected = f"{event.fighter.character.name}'s turn has ended."
        assert format_event_message(event) == expected


class TestFormatRoundEnded:
    def test_message(self):
        event = RoundEndedFactory()
        expected = f"Round {event.round_number} has ended."
        assert format_event_message(event) == expected


class TestFormatCombatEnded:
    def test_message(self):
        from .factories import CombatEndedFactory

        event = CombatEndedFactory()
        assert format_event_message(event) == "Combat has ended."


class TestFormatSpellCast:
    def test_no_targets(self):
        game = GameFactory()
        author = ActorFactory()
        caster = CharacterFactory(name="Gandalf")
        spell = SpellSettingsFactory(name="Fireball")
        event = SpellCast.objects.create(
            game=game, author=author, caster=caster, spell=spell, slot_level=3
        )
        message = format_event_message(event)
        assert "Gandalf cast Fireball" in message

    def test_with_targets(self):
        game = GameFactory()
        author = ActorFactory()
        caster = CharacterFactory(name="Gandalf")
        spell = SpellSettingsFactory(name="Fireball")
        event = SpellCast.objects.create(
            game=game, author=author, caster=caster, spell=spell, slot_level=3
        )
        target1 = CharacterFactory(name="Goblin")
        target2 = CharacterFactory(name="Orc")
        event.targets.add(target1, target2)
        message = format_event_message(event)
        assert "Gandalf cast Fireball on" in message
        assert "Goblin" in message
        assert "Orc" in message


class TestFormatSpellDamageDealt:
    def test_message(self):
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
        message = format_event_message(event)
        assert "Goblin took 28 fire damage from Fireball" in message


class TestFormatSpellHealingReceived:
    def test_message(self):
        game = GameFactory()
        author = ActorFactory()
        spell = SpellSettingsFactory(name="Cure Wounds")
        target = CharacterFactory(name="Fighter")
        event = SpellHealingReceived.objects.create(
            game=game, author=author, spell=spell, target=target, healing=12
        )
        message = format_event_message(event)
        assert "Fighter was healed for 12 HP by Cure Wounds" in message


class TestFormatSpellConditionApplied:
    def test_message(self):
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
        message = format_event_message(event)
        assert "Bandit is now" in message
        assert "Hold Person" in message


class TestFormatSpellSavingThrow:
    def test_success(self):
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
        message = format_event_message(event)
        assert "Rogue succeeded" in message
        assert "DEX save" in message
        assert "DC 15" in message
        assert "Fireball" in message
        assert "18" in message

    def test_failure(self):
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
        message = format_event_message(event)
        assert "Warrior failed" in message
        assert "WIS save" in message
        assert "DC 14" in message
        assert "Hold Person" in message
        assert "10" in message


class TestFormatDiceRoll:
    def test_basic(self):
        event = DiceRollFactory()
        message = format_event_message(event)
        assert "2d6" in message
        assert "[3, 4]" in message
        assert "7" in message

    def test_with_positive_modifier(self):
        event = DiceRollFactory(
            dice_notation="1d20",
            dice_type=20,
            num_dice=1,
            modifier=5,
            individual_rolls=[15],
            total=20,
        )
        message = format_event_message(event)
        assert "+5" in message
        assert "20" in message

    def test_with_negative_modifier(self):
        event = DiceRollFactory(
            dice_notation="1d20",
            dice_type=20,
            num_dice=1,
            modifier=-2,
            individual_rolls=[10],
            total=8,
        )
        message = format_event_message(event)
        assert "-2" in message
        assert "8" in message

    def test_with_purpose(self):
        event = DiceRollFactory(roll_purpose="Perception check")
        message = format_event_message(event)
        assert "for Perception check" in message

    def test_from_master(self):
        game = GameFactory()
        author = ActorFactory()
        author.master = game.master
        event = DiceRollFactory(game=game, author=author)
        message = format_event_message(event)
        assert "The Master" in message

    def test_from_player(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        event = DiceRollFactory(game=game, author=player)
        message = format_event_message(event)
        assert str(player) in message
