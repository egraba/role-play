import pytest
from django.urls import reverse

from game.constants.combat import ActionType, CombatAction, CombatState
from game.models.combat import Combat, Turn
from game.models.game import Player

from ..factories import GameFactory
from character.tests.factories import CharacterFactory
from user.tests.factories import UserFactory


pytestmark = pytest.mark.django_db


class TestTakeActionView:
    """Tests for TakeActionView."""

    @pytest.fixture
    def active_combat_setup(self):
        """Set up an active combat where a player can take actions."""
        game = GameFactory()
        # Create user and character with the same user
        user = UserFactory()
        character = CharacterFactory(user=user)
        # Create player linking user, game, and character
        player = Player.objects.create(user=user, game=game, character=character)
        combat = Combat.objects.create(game=game)
        # Import factory to create fighter with initiative
        from ..factories import FighterFactory

        fighter = FighterFactory(
            combat=combat,
            player=player,
            character=character,
            dexterity_check=15,
        )
        combat.start_combat()
        return {"game": game, "combat": combat, "player": player, "fighter": fighter}

    def test_take_action_success(self, client, active_combat_setup):
        """Test successfully taking an action."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"action": CombatAction.ATTACK, "action_type": ActionType.ACTION},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "action_id" in data

    def test_take_action_not_your_turn(self, client, active_combat_setup):
        """Test that taking action fails when not your turn."""
        setup = active_combat_setup
        # Create another player who is not the current fighter
        other_user = UserFactory()
        other_character = CharacterFactory(user=other_user)
        other_player = Player.objects.create(
            user=other_user, game=setup["game"], character=other_character
        )
        client.force_login(other_player.user)

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"action": CombatAction.ATTACK, "action_type": ActionType.ACTION},
        )

        assert response.status_code == 403

    def test_take_action_twice_fails(self, client, active_combat_setup):
        """Test that taking action twice fails."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )

        # First action should succeed
        response1 = client.post(
            url,
            {"action": CombatAction.ATTACK, "action_type": ActionType.ACTION},
        )
        assert response1.status_code == 200

        # Second action should fail
        response2 = client.post(
            url,
            {"action": CombatAction.DODGE, "action_type": ActionType.ACTION},
        )
        assert response2.status_code == 400
        assert "already used" in response2.json()["message"]

    def test_take_bonus_action_success(self, client, active_combat_setup):
        """Test successfully taking a bonus action."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"action": CombatAction.DASH, "action_type": ActionType.BONUS_ACTION},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_invalid_action(self, client, active_combat_setup):
        """Test that invalid action returns error."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"action": "invalid_action", "action_type": ActionType.ACTION},
        )

        assert response.status_code == 400
        assert "Invalid action" in response.json()["message"]

    def test_take_action_combat_not_active(self, client, active_combat_setup):
        """Test that action fails when combat is not active."""
        setup = active_combat_setup
        setup["combat"].state = CombatState.ROLLING_INITIATIVE
        setup["combat"].save()
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"action": CombatAction.ATTACK, "action_type": ActionType.ACTION},
        )

        assert response.status_code == 403

    def test_take_action_combat_not_found(self, client, active_combat_setup):
        """Test that action fails when combat doesn't exist."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, 99999),  # Non-existent combat ID
        )
        response = client.post(
            url,
            {"action": CombatAction.ATTACK, "action_type": ActionType.ACTION},
        )

        assert response.status_code == 403

    def test_take_action_with_valid_target(self, client, active_combat_setup):
        """Test taking action with a valid target."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        # Create another fighter as target
        other_user = UserFactory()
        other_character = CharacterFactory(user=other_user)
        other_player = Player.objects.create(
            user=other_user, game=setup["game"], character=other_character
        )
        from ..factories import FighterFactory

        target_fighter = FighterFactory(
            combat=setup["combat"],
            player=other_player,
            character=other_character,
            dexterity_check=10,
        )

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "action": CombatAction.ATTACK,
                "action_type": ActionType.ACTION,
                "target_id": target_fighter.id,
            },
        )

        assert response.status_code == 200

    def test_take_action_with_invalid_target(self, client, active_combat_setup):
        """Test taking action with invalid target returns error."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "action": CombatAction.ATTACK,
                "action_type": ActionType.ACTION,
                "target_id": 99999,  # Non-existent target
            },
        )

        assert response.status_code == 400
        assert "Invalid target" in response.json()["message"]

    def test_take_reaction_success(self, client, active_combat_setup):
        """Test successfully taking a reaction."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"action": CombatAction.ATTACK, "action_type": ActionType.REACTION},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_take_action_invalid_action_type(self, client, active_combat_setup):
        """Test that invalid action type returns error."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"action": CombatAction.ATTACK, "action_type": "invalid_type"},
        )

        assert response.status_code == 400
        assert "Invalid action type" in response.json()["message"]

    def test_take_action_no_active_turn(self, client, active_combat_setup):
        """Test that action fails when no active turn exists."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        # Mark the current turn as completed
        turn = Turn.objects.filter(
            fighter=setup["fighter"],
            round__combat=setup["combat"],
            completed=False,
        ).first()
        turn.completed = True
        turn.save()

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"action": CombatAction.ATTACK, "action_type": ActionType.ACTION},
        )

        assert response.status_code == 400
        assert "No active turn" in response.json()["message"]

    def test_take_action_no_current_fighter(self, client, active_combat_setup):
        """Test that action fails when no current fighter."""
        setup = active_combat_setup
        setup["combat"].current_fighter = None
        setup["combat"].save()
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"action": CombatAction.ATTACK, "action_type": ActionType.ACTION},
        )

        assert response.status_code == 403


class TestTurnStateView:
    """Tests for TurnStateView."""

    @pytest.fixture
    def active_combat_setup(self):
        """Set up an active combat."""
        game = GameFactory()
        user = UserFactory()
        character = CharacterFactory(user=user)
        player = Player.objects.create(user=user, game=game, character=character)
        combat = Combat.objects.create(game=game)
        from ..factories import FighterFactory

        fighter = FighterFactory(
            combat=combat,
            player=player,
            character=character,
            dexterity_check=15,
        )
        combat.start_combat()
        return {"game": game, "combat": combat, "player": player, "fighter": fighter}

    def test_get_turn_state(self, client, active_combat_setup):
        """Test getting turn state."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-turn-state",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data["fighter"] == setup["fighter"].character.name
        assert data["round"] == 1
        assert data["action_available"] is True
        assert data["bonus_action_available"] is True
        assert data["reaction_available"] is True
        assert data["movement_remaining"] == data["movement_total"]
        assert data["actions_taken"] == []

    def test_turn_state_after_action(self, client, active_combat_setup):
        """Test turn state reflects actions taken."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        # Take an action first
        action_url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        client.post(
            action_url,
            {"action": CombatAction.ATTACK, "action_type": ActionType.ACTION},
        )

        # Check turn state
        state_url = reverse(
            "combat-turn-state",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(state_url)

        assert response.status_code == 200
        data = response.json()
        assert data["action_available"] is False
        assert len(data["actions_taken"]) == 1
        assert data["actions_taken"][0]["action"] == CombatAction.ATTACK

    def test_turn_state_combat_not_active(self, client, active_combat_setup):
        """Test turn state returns error when combat not active."""
        setup = active_combat_setup
        setup["combat"].state = CombatState.ENDED
        setup["combat"].save()
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-turn-state",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        assert response.status_code == 400

    def test_turn_state_combat_not_found(self, client, active_combat_setup):
        """Test turn state returns 404 when combat doesn't exist."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-turn-state",
            args=(setup["game"].id, 99999),  # Non-existent combat
        )
        response = client.get(url)

        assert response.status_code == 404
        assert "Combat not found" in response.json()["message"]

    def test_turn_state_no_current_fighter(self, client, active_combat_setup):
        """Test turn state returns error when no current fighter."""
        setup = active_combat_setup
        setup["combat"].current_fighter = None
        setup["combat"].save()
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-turn-state",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        assert response.status_code == 400
        assert "No current fighter" in response.json()["message"]

    def test_turn_state_no_active_turn(self, client, active_combat_setup):
        """Test turn state returns error when no active turn."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        # Mark the current turn as completed
        turn = Turn.objects.filter(
            fighter=setup["fighter"],
            round__combat=setup["combat"],
            completed=False,
        ).first()
        turn.completed = True
        turn.save()

        url = reverse(
            "combat-turn-state",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        assert response.status_code == 400
        assert "No active turn" in response.json()["message"]


class TestMoveView:
    """Tests for MoveView."""

    @pytest.fixture
    def active_combat_setup(self):
        """Set up an active combat where a player can move."""
        game = GameFactory()
        user = UserFactory()
        character = CharacterFactory(user=user)
        player = Player.objects.create(user=user, game=game, character=character)
        combat = Combat.objects.create(game=game)
        from ..factories import FighterFactory

        fighter = FighterFactory(
            combat=combat,
            player=player,
            character=character,
            dexterity_check=15,
        )
        combat.start_combat()
        return {"game": game, "combat": combat, "player": player, "fighter": fighter}

    def test_move_success(self, client, active_combat_setup):
        """Test successfully using movement."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-move",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(url, {"feet": 15})

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["feet_moved"] == 15

    def test_move_limited_by_remaining(self, client, active_combat_setup):
        """Test movement is limited by remaining movement."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-move",
            args=(setup["game"].id, setup["combat"].id),
        )

        # Use most of movement
        client.post(url, {"feet": 25})

        # Try to move more than remaining
        response = client.post(url, {"feet": 20})

        assert response.status_code == 200
        data = response.json()
        assert data["feet_moved"] == 5  # Only 5 remaining
        assert data["movement_remaining"] == 0

    def test_move_invalid_feet(self, client, active_combat_setup):
        """Test that invalid feet value returns error."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-move",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(url, {"feet": -5})

        assert response.status_code == 400

    def test_move_not_your_turn(self, client, active_combat_setup):
        """Test that moving fails when not your turn."""
        setup = active_combat_setup
        other_user = UserFactory()
        other_character = CharacterFactory(user=other_user)
        other_player = Player.objects.create(
            user=other_user, game=setup["game"], character=other_character
        )
        client.force_login(other_player.user)

        url = reverse(
            "combat-move",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(url, {"feet": 15})

        assert response.status_code == 403

    def test_move_combat_not_active(self, client, active_combat_setup):
        """Test that moving fails when combat is not active."""
        setup = active_combat_setup
        setup["combat"].state = CombatState.ROLLING_INITIATIVE
        setup["combat"].save()
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-move",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(url, {"feet": 15})

        assert response.status_code == 403

    def test_move_combat_not_found(self, client, active_combat_setup):
        """Test that moving fails when combat doesn't exist."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-move",
            args=(setup["game"].id, 99999),  # Non-existent combat
        )
        response = client.post(url, {"feet": 15})

        assert response.status_code == 403

    def test_move_non_integer_feet(self, client, active_combat_setup):
        """Test that non-integer feet value returns error."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-move",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(url, {"feet": "abc"})

        assert response.status_code == 400
        assert "Invalid feet value" in response.json()["message"]

    def test_move_no_current_fighter(self, client, active_combat_setup):
        """Test that moving fails when no current fighter."""
        setup = active_combat_setup
        setup["combat"].current_fighter = None
        setup["combat"].save()
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-move",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(url, {"feet": 15})

        assert response.status_code == 403

    def test_move_no_active_turn(self, client, active_combat_setup):
        """Test that moving fails when no active turn exists."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        # Mark the current turn as completed
        turn = Turn.objects.filter(
            fighter=setup["fighter"],
            round__combat=setup["combat"],
            completed=False,
        ).first()
        turn.completed = True
        turn.save()

        url = reverse(
            "combat-move",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(url, {"feet": 15})

        assert response.status_code == 400
        assert "No active turn" in response.json()["message"]

    def test_move_zero_feet(self, client, active_combat_setup):
        """Test that zero feet value returns error."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-move",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(url, {"feet": 0})

        assert response.status_code == 400
        assert "Feet must be positive" in response.json()["message"]
