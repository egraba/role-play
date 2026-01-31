import pytest
from django.urls import reverse

from game.constants.combat import CombatAction
from game.models.combat import Combat
from game.models.game import Player

from ..factories import GameFactory, FighterFactory
from character.tests.factories import CharacterFactory
from user.tests.factories import UserFactory


pytestmark = pytest.mark.django_db


class TestActionPanelView:
    """Tests for ActionPanelView."""

    @pytest.fixture
    def active_combat_setup(self):
        """Set up an active combat with multiple fighters."""
        game = GameFactory()
        # Create first user/character/player (current turn)
        user1 = UserFactory()
        character1 = CharacterFactory(user=user1)
        player1 = Player.objects.create(user=user1, game=game, character=character1)

        # Create second user/character/player
        user2 = UserFactory()
        character2 = CharacterFactory(user=user2)
        player2 = Player.objects.create(user=user2, game=game, character=character2)

        combat = Combat.objects.create(game=game)
        fighter1 = FighterFactory(
            combat=combat,
            player=player1,
            character=character1,
            dexterity_check=15,
        )
        fighter2 = FighterFactory(
            combat=combat,
            player=player2,
            character=character2,
            dexterity_check=10,
        )
        combat.start_combat()
        return {
            "game": game,
            "combat": combat,
            "player1": player1,
            "player2": player2,
            "fighter1": fighter1,
            "fighter2": fighter2,
        }

    def test_view_returns_html(self, client, active_combat_setup):
        """Test action panel returns HTML content."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "action-panel",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        assert response.status_code == 200
        assert "action-panel" in response.content.decode()

    def test_panel_shows_action_buttons(self, client, active_combat_setup):
        """Test panel displays all action buttons."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "action-panel",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        assert "Attack" in content
        assert "Cast Spell" in content
        assert "Dash" in content
        assert "Dodge" in content
        assert "Help" in content
        assert "Hide" in content

    def test_panel_shows_your_turn_badge_for_current_player(
        self, client, active_combat_setup
    ):
        """Test panel shows 'Your Turn' badge for current player."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "action-panel",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        assert "Your Turn" in content

    def test_panel_disabled_for_non_current_player(self, client, active_combat_setup):
        """Test panel is disabled when not your turn."""
        setup = active_combat_setup
        # Player2 is not current (fighter1 has higher initiative)
        client.force_login(setup["player2"].user)

        url = reverse(
            "action-panel",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        assert "panel-disabled" in content
        assert "Your Turn" not in content

    def test_panel_shows_movement_bar(self, client, active_combat_setup):
        """Test panel displays movement bar with correct values."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "action-panel",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        assert "Movement" in content
        assert "ft" in content

    def test_panel_shows_action_as_used_after_taking_action(
        self, client, active_combat_setup
    ):
        """Test panel shows action as used after taking an action."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        # Take an action first
        action_url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        client.post(
            action_url,
            {"action": CombatAction.ATTACK, "action_type": "A"},
        )

        # Check panel
        panel_url = reverse(
            "action-panel",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(panel_url)

        content = response.content.decode()
        assert "status-used" in content

    def test_panel_shows_actions_taken_log(self, client, active_combat_setup):
        """Test panel displays actions taken during turn."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        # Take an action first
        action_url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        client.post(
            action_url,
            {"action": CombatAction.ATTACK, "action_type": "A"},
        )

        # Check panel
        panel_url = reverse(
            "action-panel",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(panel_url)

        content = response.content.decode()
        assert "Actions Taken" in content
        assert "Attack" in content

    def test_panel_returns_empty_for_inactive_combat(self, client, active_combat_setup):
        """Test panel returns empty response for inactive combat."""
        setup = active_combat_setup
        setup["combat"].end_combat()
        client.force_login(setup["player1"].user)

        url = reverse(
            "action-panel",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.content == b""

    def test_panel_returns_empty_for_nonexistent_combat(
        self, client, active_combat_setup
    ):
        """Test panel returns empty for non-existent combat."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "action-panel",
            args=(setup["game"].id, 99999),
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.content == b""

    def test_panel_shows_bonus_action_section(self, client, active_combat_setup):
        """Test panel displays bonus action section."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "action-panel",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        assert "Bonus Action" in content

    def test_panel_shows_reaction_section(self, client, active_combat_setup):
        """Test panel displays reaction section."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "action-panel",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        assert "Reaction" in content

    def test_panel_movement_updates_after_moving(self, client, active_combat_setup):
        """Test movement display updates after using movement."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        # Use some movement
        move_url = reverse(
            "combat-move",
            args=(setup["game"].id, setup["combat"].id),
        )
        client.post(move_url, {"feet": 15})

        # Check panel
        panel_url = reverse(
            "action-panel",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(panel_url)

        content = response.content.decode()
        # Should show reduced movement (30 - 15 = 15)
        assert "15" in content


class TestTakeActionViewHTMX:
    """Tests for TakeActionView HTMX responses."""

    @pytest.fixture
    def active_combat_setup(self):
        """Set up an active combat where a player can take actions."""
        game = GameFactory()
        user = UserFactory()
        character = CharacterFactory(user=user)
        player = Player.objects.create(user=user, game=game, character=character)
        combat = Combat.objects.create(game=game)
        fighter = FighterFactory(
            combat=combat,
            player=player,
            character=character,
            dexterity_check=15,
        )
        combat.start_combat()
        return {"game": game, "combat": combat, "player": player, "fighter": fighter}

    def test_htmx_request_returns_html(self, client, active_combat_setup):
        """Test HTMX request returns HTML instead of JSON."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"action": CombatAction.ATTACK, "action_type": "A"},
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert "action-panel" in content
        # Should not be JSON
        assert "status" not in content or '"status"' not in content

    def test_htmx_request_sets_trigger_header(self, client, active_combat_setup):
        """Test HTMX request sets HX-Trigger header."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"action": CombatAction.ATTACK, "action_type": "A"},
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 200
        assert response["HX-Trigger"] == "action-taken"

    def test_htmx_request_shows_action_used(self, client, active_combat_setup):
        """Test HTMX response shows action as used."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"action": CombatAction.ATTACK, "action_type": "A"},
            HTTP_HX_REQUEST="true",
        )

        content = response.content.decode()
        assert "status-used" in content

    def test_non_htmx_request_returns_json(self, client, active_combat_setup):
        """Test non-HTMX request still returns JSON."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"action": CombatAction.ATTACK, "action_type": "A"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_htmx_error_returns_text(self, client, active_combat_setup):
        """Test HTMX request returns text error instead of JSON."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-take-action",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"action": "invalid_action", "action_type": "A"},
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 400
        assert b"Invalid action" in response.content


class TestMoveViewHTMX:
    """Tests for MoveView HTMX responses."""

    @pytest.fixture
    def active_combat_setup(self):
        """Set up an active combat where a player can move."""
        game = GameFactory()
        user = UserFactory()
        character = CharacterFactory(user=user)
        player = Player.objects.create(user=user, game=game, character=character)
        combat = Combat.objects.create(game=game)
        fighter = FighterFactory(
            combat=combat,
            player=player,
            character=character,
            dexterity_check=15,
        )
        combat.start_combat()
        return {"game": game, "combat": combat, "player": player, "fighter": fighter}

    def test_htmx_request_returns_html(self, client, active_combat_setup):
        """Test HTMX request returns HTML instead of JSON."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-move",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"feet": 15},
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert "action-panel" in content

    def test_htmx_response_shows_updated_movement(self, client, active_combat_setup):
        """Test HTMX response shows updated movement."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-move",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"feet": 15},
            HTTP_HX_REQUEST="true",
        )

        content = response.content.decode()
        # Should show 15 remaining (30 - 15)
        assert "15" in content

    def test_non_htmx_request_returns_json(self, client, active_combat_setup):
        """Test non-HTMX request still returns JSON."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-move",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"feet": 15},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["feet_moved"] == 15

    def test_htmx_error_returns_text(self, client, active_combat_setup):
        """Test HTMX request returns text error instead of JSON."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-move",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {"feet": "invalid"},
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 400
        assert b"Invalid feet value" in response.content

    def test_htmx_move_all_remaining(self, client, active_combat_setup):
        """Test HTMX move with all remaining movement."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-move",
            args=(setup["game"].id, setup["combat"].id),
        )

        # Move all 30 feet
        response = client.post(
            url,
            {"feet": 30},
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 200
        content = response.content.decode()
        # Should show 0 remaining
        assert "0/30" in content or "0 ft" in content or "depleted" in content
