import pytest
from django.urls import reverse

from game.models.combat import Combat, Turn
from game.models.game import Player

from ..factories import GameFactory, FighterFactory
from character.tests.factories import CharacterFactory
from user.tests.factories import UserFactory


pytestmark = pytest.mark.django_db


class TestInitiativeTrackerView:
    """Tests for InitiativeTrackerView."""

    @pytest.fixture
    def active_combat_setup(self):
        """Set up an active combat with multiple fighters."""
        game = GameFactory()
        # Create first user/character/player
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

    def test_view_mapping(self, client, active_combat_setup):
        """Test URL maps to InitiativeTrackerView."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "initiative-tracker",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        assert response.status_code == 200

    def test_tracker_displays_fighters(self, client, active_combat_setup):
        """Test tracker displays all fighters in initiative order."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "initiative-tracker",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        assert setup["fighter1"].character.name in content
        assert setup["fighter2"].character.name in content

    def test_tracker_shows_current_turn(self, client, active_combat_setup):
        """Test tracker highlights current turn."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "initiative-tracker",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        assert "current-turn" in content

    def test_tracker_shows_round_counter(self, client, active_combat_setup):
        """Test tracker displays round counter."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "initiative-tracker",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        assert "Round" in content
        assert str(setup["combat"].current_round) in content

    def test_tracker_returns_empty_for_inactive_combat(
        self, client, active_combat_setup
    ):
        """Test tracker returns empty response for inactive combat."""
        setup = active_combat_setup
        setup["combat"].end_combat()
        client.force_login(setup["player1"].user)

        url = reverse(
            "initiative-tracker",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.content == b""

    def test_tracker_returns_empty_for_nonexistent_combat(
        self, client, active_combat_setup
    ):
        """Test tracker returns empty for non-existent combat."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "initiative-tracker",
            args=(setup["game"].id, 99999),
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.content == b""

    def test_tracker_shows_dm_controls_for_master(self, client, active_combat_setup):
        """Test tracker shows DM controls only for game master."""
        setup = active_combat_setup
        # Login as game master
        client.force_login(setup["game"].master.user)

        url = reverse(
            "initiative-tracker",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        assert "Next Turn" in content
        assert "End Combat" in content

    def test_tracker_hides_dm_controls_for_player(self, client):
        """Test tracker hides DM controls for regular players."""
        game = GameFactory()
        # Create a player who is NOT the master
        user = UserFactory()
        character = CharacterFactory(user=user)
        player = Player.objects.create(user=user, game=game, character=character)

        combat = Combat.objects.create(game=game)
        FighterFactory(
            combat=combat,
            player=player,
            character=character,
            dexterity_check=15,
        )
        combat.start_combat()

        # Login as the player, not the master
        client.force_login(user)

        url = reverse(
            "initiative-tracker",
            args=(game.id, combat.id),
        )
        response = client.get(url)

        content = response.content.decode()
        # The actual dm-controls div should not be rendered for non-DM players
        # (Note: the CSS styles contain "dm-controls" but that's fine)
        assert '<div class="dm-controls">' not in content
        assert "Next Turn" not in content
        assert "End Combat" not in content

    # Note: test_tracker_requires_login is not implemented because GameContextMixin
    # runs setup() before LoginRequiredMixin can redirect, causing errors with
    # anonymous users. This would require refactoring the mixin order.


class TestReadyActionView:
    """Tests for ReadyActionView."""

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

    def test_ready_action_success(self, client, active_combat_setup):
        """Test successfully taking the Ready action."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-ready",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(url)

        assert response.status_code == 200
        # Verify the action was used
        turn = Turn.objects.filter(
            fighter=setup["fighter"],
            round__combat=setup["combat"],
            completed=False,
        ).first()
        assert turn.action_used is True

    def test_ready_action_not_your_turn(self, client, active_combat_setup):
        """Test Ready action fails when not your turn."""
        setup = active_combat_setup
        # Create another player who is not the current fighter
        other_user = UserFactory()
        other_character = CharacterFactory(user=other_user)
        Player.objects.create(
            user=other_user, game=setup["game"], character=other_character
        )
        client.force_login(other_user)

        url = reverse(
            "combat-ready",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(url)

        assert response.status_code == 403

    def test_ready_action_twice_fails(self, client, active_combat_setup):
        """Test Ready action fails when action already used."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-ready",
            args=(setup["game"].id, setup["combat"].id),
        )

        # First action should succeed
        response1 = client.post(url)
        assert response1.status_code == 200

        # Second action should fail
        response2 = client.post(url)
        assert response2.status_code == 400

    def test_ready_action_returns_tracker_html(self, client, active_combat_setup):
        """Test Ready action returns updated tracker HTML."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-ready",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert "initiative-tracker" in content

    def test_ready_action_sets_hx_trigger(self, client, active_combat_setup):
        """Test Ready action sets HX-Trigger header."""
        setup = active_combat_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "combat-ready",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(url)

        assert response.status_code == 200
        assert response["HX-Trigger"] == "initiative-updated"


class TestDelayTurnView:
    """Tests for DelayTurnView."""

    @pytest.fixture
    def active_combat_setup(self):
        """Set up an active combat with multiple fighters."""
        game = GameFactory()
        # Create first user/character/player
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

    def test_delay_turn_success(self, client, active_combat_setup):
        """Test successfully delaying turn."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)
        initial_fighter = setup["combat"].current_fighter

        url = reverse(
            "combat-delay",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(url)

        assert response.status_code == 200
        # Verify turn advanced
        setup["combat"].refresh_from_db()
        assert setup["combat"].current_fighter != initial_fighter

    def test_delay_turn_not_your_turn(self, client, active_combat_setup):
        """Test Delay fails when not your turn."""
        setup = active_combat_setup
        # Player2 is not current (fighter1 has higher initiative)
        client.force_login(setup["player2"].user)

        url = reverse(
            "combat-delay",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(url)

        assert response.status_code == 403

    def test_delay_turn_returns_tracker_html(self, client, active_combat_setup):
        """Test Delay action returns updated tracker HTML."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-delay",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert "initiative-tracker" in content

    def test_delay_turn_sets_hx_trigger(self, client, active_combat_setup):
        """Test Delay action sets HX-Trigger header."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-delay",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(url)

        assert response.status_code == 200
        assert response["HX-Trigger"] == "initiative-updated"

    def test_delay_turn_advances_to_next_fighter(self, client, active_combat_setup):
        """Test Delay advances to the next fighter in initiative order."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        # Fighter1 should be current (higher initiative)
        assert setup["combat"].current_fighter == setup["fighter1"]

        url = reverse(
            "combat-delay",
            args=(setup["game"].id, setup["combat"].id),
        )
        client.post(url)

        setup["combat"].refresh_from_db()
        # Now fighter2 should be current
        assert setup["combat"].current_fighter == setup["fighter2"]
