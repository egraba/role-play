import pytest

from game.constants.combat import ActionType, CombatAction, CombatState
from game.exceptions import ActionNotAvailable
from game.models.combat import Combat, Fighter, Round, Turn, TurnAction

from ..factories import CombatFactory, FighterFactory, GameFactory, PlayerFactory

pytestmark = pytest.mark.django_db


class TestCombatModel:
    @pytest.fixture
    def combat(self):
        return CombatFactory()

    @pytest.fixture
    def combat_with_pending_initiative(self):
        """Create a combat where fighters haven't rolled initiative yet."""
        game = GameFactory()
        combat = Combat.objects.create(game=game)
        player1 = PlayerFactory(game=game)
        player2 = PlayerFactory(game=game)
        FighterFactory(
            combat=combat,
            player=player1,
            character=player1.character,
            dexterity_check=None,
        )
        FighterFactory(
            combat=combat,
            player=player2,
            character=player2.character,
            dexterity_check=None,
        )
        return combat

    def test_get_initiative_order(self, combat):
        fighters = list(
            Fighter.objects.filter(combat=combat).order_by("-dexterity_check")
        )
        assert combat.get_initiative_order() == fighters

    def test_all_initiative_rolled_false(self, combat_with_pending_initiative):
        """Test that all_initiative_rolled returns False when initiative not rolled."""
        assert combat_with_pending_initiative.all_initiative_rolled() is False

    def test_all_initiative_rolled_true(self, combat):
        """Test that all_initiative_rolled returns True when all have rolled."""
        # CombatFactory creates fighters with dexterity_check set
        assert combat.all_initiative_rolled() is True

    def test_start_combat(self, combat):
        """Test starting combat after all initiative rolled."""
        first_fighter = combat.start_combat()

        assert first_fighter is not None
        assert combat.state == CombatState.ACTIVE
        assert combat.current_round == 1
        assert combat.current_turn_index == 0
        assert combat.current_fighter == first_fighter
        # First fighter should have highest dexterity check
        assert first_fighter == combat.get_initiative_order()[0]
        # Round should be created
        assert Round.objects.filter(combat=combat, number=1).exists()

    def test_start_combat_fails_without_initiative(
        self, combat_with_pending_initiative
    ):
        """Test that start_combat returns None if initiative not rolled."""
        result = combat_with_pending_initiative.start_combat()

        assert result is None
        assert combat_with_pending_initiative.state == CombatState.ROLLING_INITIATIVE

    def test_advance_turn_same_round(self, combat):
        """Test advancing turn within the same round."""
        combat.start_combat()
        first_fighter = combat.current_fighter

        next_fighter, is_new_round = combat.advance_turn()

        assert is_new_round is False
        assert next_fighter != first_fighter
        assert combat.current_turn_index == 1
        assert combat.current_round == 1

    def test_advance_turn_new_round(self, combat):
        """Test advancing turn to a new round."""
        combat.start_combat()
        num_fighters = len(combat.get_initiative_order())

        # Advance through all fighters
        for _ in range(num_fighters - 1):
            combat.advance_turn()

        # This should trigger a new round
        _, is_new_round = combat.advance_turn()

        assert is_new_round is True
        assert combat.current_round == 2
        assert combat.current_turn_index == 0
        assert Round.objects.filter(combat=combat, number=2).exists()

    def test_advance_turn_not_active(self, combat):
        """Test that advance_turn returns None if combat not active."""
        # Combat hasn't started yet
        next_fighter, is_new_round = combat.advance_turn()

        assert next_fighter is None
        assert is_new_round is False

    def test_end_combat(self, combat):
        """Test ending combat."""
        combat.start_combat()

        combat.end_combat()

        assert combat.state == CombatState.ENDED
        assert combat.current_fighter is None

    def test_get_turn_order_display(self, combat):
        """Test getting turn order for display."""
        combat.start_combat()

        display = combat.get_turn_order_display()

        assert len(display) == len(combat.get_initiative_order())
        # First item should be marked as current
        assert display[0]["is_current"] is True
        for item in display:
            assert "fighter" in item
            assert "initiative" in item
            assert "is_current" in item
            assert "is_surprised" in item

    def test_start_combat_no_fighters(self):
        """Test that start_combat returns None when no fighters exist."""
        game = GameFactory()
        combat = Combat.objects.create(game=game)
        # No fighters, so all_initiative_rolled returns True (no pending)

        result = combat.start_combat()

        assert result is None

    def test_advance_turn_no_fighters(self):
        """Test that advance_turn returns None when no fighters exist in active combat."""
        game = GameFactory()
        combat = Combat.objects.create(game=game, state=CombatState.ACTIVE)

        next_fighter, is_new_round = combat.advance_turn()

        assert next_fighter is None
        assert is_new_round is False


class TestRoundModel:
    def test_str(self):
        """Test Round string representation."""
        game = GameFactory()
        combat = Combat.objects.create(game=game)
        round_obj = Round.objects.create(combat=combat, number=3)

        assert str(round_obj) == "Round 3"


class TestTurnModel:
    @pytest.fixture
    def turn_with_fighter(self):
        """Create a turn with a fighter for testing."""
        game = GameFactory()
        combat = Combat.objects.create(game=game)
        round_obj = Round.objects.create(combat=combat, number=1)
        player = PlayerFactory(game=game)
        fighter = FighterFactory(
            combat=combat,
            player=player,
            character=player.character,
            dexterity_check=10,
        )
        turn = Turn.objects.create(fighter=fighter, round=round_obj, movement_total=30)
        return turn

    def test_str(self):
        """Test Turn string representation."""
        game = GameFactory()
        combat = Combat.objects.create(game=game)
        round_obj = Round.objects.create(combat=combat, number=2)
        player = PlayerFactory(game=game)
        fighter = FighterFactory(
            combat=combat,
            player=player,
            character=player.character,
            dexterity_check=10,
        )
        turn = Turn.objects.create(fighter=fighter, round=round_obj)

        assert str(turn) == f"{fighter} - Round 2"

    def test_can_take_action_initially_true(self, turn_with_fighter):
        """Test that action is available at start of turn."""
        assert turn_with_fighter.can_take_action() is True

    def test_can_take_bonus_action_initially_true(self, turn_with_fighter):
        """Test that bonus action is available at start of turn."""
        assert turn_with_fighter.can_take_bonus_action() is True

    def test_can_take_reaction_initially_true(self, turn_with_fighter):
        """Test that reaction is available at start of turn."""
        assert turn_with_fighter.can_take_reaction() is True

    def test_remaining_movement_initially_full(self, turn_with_fighter):
        """Test that full movement is available at start of turn."""
        assert turn_with_fighter.remaining_movement() == 30

    def test_use_action(self, turn_with_fighter):
        """Test using the standard action."""
        turn_action = turn_with_fighter.use_action(CombatAction.ATTACK)

        assert turn_with_fighter.action_used is True
        assert turn_with_fighter.can_take_action() is False
        assert turn_action.action_type == ActionType.ACTION
        assert turn_action.action == CombatAction.ATTACK

    def test_use_action_twice_raises_error(self, turn_with_fighter):
        """Test that using action twice raises ActionNotAvailable."""
        turn_with_fighter.use_action(CombatAction.ATTACK)

        with pytest.raises(ActionNotAvailable):
            turn_with_fighter.use_action(CombatAction.DODGE)

    def test_use_bonus_action(self, turn_with_fighter):
        """Test using the bonus action."""
        turn_action = turn_with_fighter.use_bonus_action(CombatAction.DASH)

        assert turn_with_fighter.bonus_action_used is True
        assert turn_with_fighter.can_take_bonus_action() is False
        assert turn_action.action_type == ActionType.BONUS_ACTION

    def test_use_bonus_action_twice_raises_error(self, turn_with_fighter):
        """Test that using bonus action twice raises ActionNotAvailable."""
        turn_with_fighter.use_bonus_action(CombatAction.DASH)

        with pytest.raises(ActionNotAvailable):
            turn_with_fighter.use_bonus_action(CombatAction.HIDE)

    def test_use_reaction(self, turn_with_fighter):
        """Test using the reaction."""
        turn_action = turn_with_fighter.use_reaction(CombatAction.ATTACK)

        assert turn_with_fighter.reaction_used is True
        assert turn_with_fighter.can_take_reaction() is False
        assert turn_action.action_type == ActionType.REACTION

    def test_use_reaction_twice_raises_error(self, turn_with_fighter):
        """Test that using reaction twice raises ActionNotAvailable."""
        turn_with_fighter.use_reaction(CombatAction.ATTACK)

        with pytest.raises(ActionNotAvailable):
            turn_with_fighter.use_reaction(CombatAction.ATTACK)

    def test_use_movement(self, turn_with_fighter):
        """Test using movement."""
        actual = turn_with_fighter.use_movement(15)

        assert actual == 15
        assert turn_with_fighter.movement_used == 15
        assert turn_with_fighter.remaining_movement() == 15

    def test_use_movement_limited_by_remaining(self, turn_with_fighter):
        """Test that movement is limited by remaining movement."""
        turn_with_fighter.use_movement(25)
        actual = turn_with_fighter.use_movement(10)

        assert actual == 5  # Only 5 remaining
        assert turn_with_fighter.movement_used == 30
        assert turn_with_fighter.remaining_movement() == 0

    def test_use_action_with_target(self, turn_with_fighter):
        """Test using action with a target."""
        # Create another fighter as target
        game = turn_with_fighter.round.combat.game
        player2 = PlayerFactory(game=game)
        target = FighterFactory(
            combat=turn_with_fighter.round.combat,
            player=player2,
            character=player2.character,
            dexterity_check=5,
        )

        turn_action = turn_with_fighter.use_action(CombatAction.ATTACK, target)

        assert turn_action.target_fighter == target


class TestFighterModel:
    def test_str(self):
        """Test Fighter string representation."""
        game = GameFactory()
        player = PlayerFactory(game=game)
        combat = Combat.objects.create(game=game)
        fighter = FighterFactory(
            combat=combat,
            player=player,
            character=player.character,
            dexterity_check=15,
        )

        assert str(fighter) == player.character.name


class TestTurnActionModel:
    def test_str_without_target(self):
        """Test TurnAction string representation without target."""
        game = GameFactory()
        combat = Combat.objects.create(game=game)
        round_obj = Round.objects.create(combat=combat, number=1)
        player = PlayerFactory(game=game)
        fighter = FighterFactory(
            combat=combat, player=player, character=player.character, dexterity_check=10
        )
        turn = Turn.objects.create(fighter=fighter, round=round_obj)
        turn_action = TurnAction.objects.create(
            turn=turn, action_type=ActionType.ACTION, action=CombatAction.DODGE
        )

        assert str(turn_action) == "Dodge"

    def test_str_with_target(self):
        """Test TurnAction string representation with target."""
        game = GameFactory()
        combat = Combat.objects.create(game=game)
        round_obj = Round.objects.create(combat=combat, number=1)
        player1 = PlayerFactory(game=game)
        player2 = PlayerFactory(game=game)
        fighter = FighterFactory(
            combat=combat,
            player=player1,
            character=player1.character,
            dexterity_check=10,
        )
        target = FighterFactory(
            combat=combat,
            player=player2,
            character=player2.character,
            dexterity_check=5,
        )
        turn = Turn.objects.create(fighter=fighter, round=round_obj)
        turn_action = TurnAction.objects.create(
            turn=turn,
            action_type=ActionType.ACTION,
            action=CombatAction.ATTACK,
            target_fighter=target,
        )

        assert str(turn_action) == f"Attack -> {target}"


class TestCombatTurnCreation:
    """Tests for Turn creation during combat start and advancement."""

    def test_start_combat_creates_turn(self):
        """Test that start_combat creates a Turn for the first fighter."""
        combat = CombatFactory()
        combat.start_combat()

        first_fighter = combat.current_fighter
        turn = Turn.objects.filter(
            fighter=first_fighter, round__combat=combat, completed=False
        ).first()

        assert turn is not None
        assert turn.fighter == first_fighter
        assert turn.action_used is False
        assert turn.bonus_action_used is False
        assert turn.reaction_used is False

    def test_advance_turn_completes_current_and_creates_new(self):
        """Test that advance_turn completes current turn and creates new one."""
        combat = CombatFactory()
        combat.start_combat()
        first_fighter = combat.current_fighter

        # Get the first turn
        first_turn = Turn.objects.filter(
            fighter=first_fighter, round__combat=combat
        ).first()

        # Advance to next fighter
        next_fighter, _ = combat.advance_turn()

        # First turn should be completed
        first_turn.refresh_from_db()
        assert first_turn.completed is True

        # New turn should exist for next fighter
        new_turn = Turn.objects.filter(
            fighter=next_fighter, round__combat=combat, completed=False
        ).first()
        assert new_turn is not None
        assert new_turn.fighter == next_fighter
