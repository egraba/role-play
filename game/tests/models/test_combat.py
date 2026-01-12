import pytest

from game.constants.combat import CombatState
from game.models.combat import Combat, Fighter, Round, Turn

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
