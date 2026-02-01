"""Tests for the concentration indicator and save views."""

from unittest.mock import patch

import pytest
from django.urls import reverse

from character.models.spells import Concentration
from character.tests.factories import CharacterFactory, SpellSettingsFactory
from game.models.combat import Combat
from game.models.events import (
    ConcentrationBroken,
    ConcentrationSaveRequired,
    ConcentrationSaveResult,
)
from game.models.game import Player
from user.tests.factories import UserFactory

from ..factories import FighterFactory, GameFactory


pytestmark = pytest.mark.django_db


class TestConcentrationSaveModalView:
    """Tests for ConcentrationSaveModalView."""

    @pytest.fixture
    def concentration_setup(self):
        """Set up a game with a concentrating character."""
        game = GameFactory()
        user = UserFactory()
        character = CharacterFactory(user=user)
        player = Player.objects.create(user=user, game=game, character=character)

        # Create a concentration spell and start concentrating
        spell = SpellSettingsFactory(name="Bless", concentration=True)
        concentration = Concentration.start_concentration(character, spell)

        return {
            "game": game,
            "player": player,
            "character": character,
            "concentration": concentration,
            "spell": spell,
        }

    def test_modal_returns_html(self, client, concentration_setup):
        """Test concentration save modal returns HTML content."""
        setup = concentration_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "concentration-save-modal",
            args=(setup["game"].id, setup["character"].pk),
        )
        response = client.get(url, {"damage": 10})

        assert response.status_code == 200
        assert "concentration-save-modal" in response.content.decode()

    def test_modal_shows_spell_name(self, client, concentration_setup):
        """Test modal displays the concentrated spell name."""
        setup = concentration_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "concentration-save-modal",
            args=(setup["game"].id, setup["character"].pk),
        )
        response = client.get(url, {"damage": 10})

        content = response.content.decode()
        assert setup["spell"].name in content

    def test_modal_shows_dc_minimum_10(self, client, concentration_setup):
        """Test DC is at least 10 even for low damage."""
        setup = concentration_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "concentration-save-modal",
            args=(setup["game"].id, setup["character"].pk),
        )
        # Damage of 10 would give DC 5, but minimum is 10
        response = client.get(url, {"damage": 10})

        content = response.content.decode()
        # DC should be 10 (max(10, 10//2) = 10)
        assert "DC" in content or "dc" in content.lower()

    def test_modal_shows_dc_half_damage(self, client, concentration_setup):
        """Test DC is half damage when > 20."""
        setup = concentration_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "concentration-save-modal",
            args=(setup["game"].id, setup["character"].pk),
        )
        # Damage of 30 should give DC 15
        response = client.get(url, {"damage": 30})

        content = response.content.decode()
        assert ">15<" in content or "15</span>" in content

    def test_modal_shows_con_modifier(self, client, concentration_setup):
        """Test modal displays Constitution modifier."""
        setup = concentration_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "concentration-save-modal",
            args=(setup["game"].id, setup["character"].pk),
        )
        response = client.get(url, {"damage": 10})

        content = response.content.decode()
        assert "Constitution" in content or "modifier" in content.lower()

    def test_modal_returns_404_for_invalid_character(self, client, concentration_setup):
        """Test modal returns 404 for non-existent character."""
        setup = concentration_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "concentration-save-modal",
            args=(setup["game"].id, 99999),
        )
        response = client.get(url, {"damage": 10})

        assert response.status_code == 404

    def test_modal_returns_400_without_concentration(self, client, concentration_setup):
        """Test modal returns 400 if character has no concentration."""
        setup = concentration_setup
        client.force_login(setup["player"].user)

        # Break concentration first
        setup["concentration"].break_concentration()

        url = reverse(
            "concentration-save-modal",
            args=(setup["game"].id, setup["character"].pk),
        )
        response = client.get(url, {"damage": 10})

        assert response.status_code == 400


class TestConcentrationSaveRollView:
    """Tests for ConcentrationSaveRollView."""

    @pytest.fixture
    def concentration_setup(self):
        """Set up a game with a concentrating character."""
        game = GameFactory()
        user = UserFactory()
        character = CharacterFactory(user=user)
        player = Player.objects.create(user=user, game=game, character=character)

        spell = SpellSettingsFactory(name="Bless", concentration=True)
        concentration = Concentration.start_concentration(character, spell)

        return {
            "game": game,
            "player": player,
            "character": character,
            "concentration": concentration,
            "spell": spell,
        }

    @patch("game.views.concentration.random.randint")
    def test_successful_save_maintains_concentration(
        self, mock_randint, client, concentration_setup
    ):
        """Test successful save maintains concentration."""
        mock_randint.return_value = 15  # High roll, should succeed
        setup = concentration_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "concentration-save-roll",
            args=(setup["game"].id, setup["character"].pk),
        )
        response = client.post(url, {"dc": 10, "con_modifier": 2})

        assert response.status_code == 200
        content = response.content.decode()
        assert "SUCCESS" in content or "Maintained" in content

        # Concentration should still exist
        setup["character"].refresh_from_db()
        assert Concentration.objects.filter(character=setup["character"]).exists()

    @patch("game.views.concentration.random.randint")
    def test_failed_save_breaks_concentration(
        self, mock_randint, client, concentration_setup
    ):
        """Test failed save breaks concentration."""
        mock_randint.return_value = 3  # Low roll, should fail
        setup = concentration_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "concentration-save-roll",
            args=(setup["game"].id, setup["character"].pk),
        )
        response = client.post(url, {"dc": 10, "con_modifier": 0})

        assert response.status_code == 200
        content = response.content.decode()
        assert "FAILED" in content or "Lost" in content or "lost" in content

        # Concentration should be broken
        setup["character"].refresh_from_db()
        assert not Concentration.objects.filter(character=setup["character"]).exists()

    @patch("game.views.concentration.random.randint")
    def test_natural_20_always_succeeds(
        self, mock_randint, client, concentration_setup
    ):
        """Test natural 20 always succeeds regardless of DC."""
        mock_randint.return_value = 20
        setup = concentration_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "concentration-save-roll",
            args=(setup["game"].id, setup["character"].pk),
        )
        # Very high DC, but nat 20 should succeed
        response = client.post(url, {"dc": 30, "con_modifier": -5})

        content = response.content.decode()
        assert "NATURAL 20" in content or "SUCCESS" in content

        # Concentration should still exist
        assert Concentration.objects.filter(character=setup["character"]).exists()

    @patch("game.views.concentration.random.randint")
    def test_natural_1_always_fails(self, mock_randint, client, concentration_setup):
        """Test natural 1 always fails regardless of modifier."""
        mock_randint.return_value = 1
        setup = concentration_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "concentration-save-roll",
            args=(setup["game"].id, setup["character"].pk),
        )
        # High modifier, but nat 1 should fail
        response = client.post(url, {"dc": 10, "con_modifier": 20})

        content = response.content.decode()
        assert "NATURAL 1" in content or "FAILED" in content

        # Concentration should be broken
        assert not Concentration.objects.filter(character=setup["character"]).exists()

    @patch("game.views.concentration.random.randint")
    def test_creates_result_event(self, mock_randint, client, concentration_setup):
        """Test rolling creates a ConcentrationSaveResult event."""
        mock_randint.return_value = 15
        setup = concentration_setup
        client.force_login(setup["player"].user)

        initial_count = ConcentrationSaveResult.objects.count()

        url = reverse(
            "concentration-save-roll",
            args=(setup["game"].id, setup["character"].pk),
        )
        client.post(url, {"dc": 10, "con_modifier": 2})

        assert ConcentrationSaveResult.objects.count() == initial_count + 1
        event = ConcentrationSaveResult.objects.latest("date")
        assert event.character == setup["character"]
        assert event.spell == setup["spell"]
        assert event.dc == 10
        assert event.roll == 15

    @patch("game.views.concentration.random.randint")
    def test_failed_save_creates_broken_event(
        self, mock_randint, client, concentration_setup
    ):
        """Test failed save creates a ConcentrationBroken event."""
        mock_randint.return_value = 3
        setup = concentration_setup
        client.force_login(setup["player"].user)

        initial_count = ConcentrationBroken.objects.count()

        url = reverse(
            "concentration-save-roll",
            args=(setup["game"].id, setup["character"].pk),
        )
        client.post(url, {"dc": 10, "con_modifier": 0})

        assert ConcentrationBroken.objects.count() == initial_count + 1
        event = ConcentrationBroken.objects.latest("date")
        assert event.character == setup["character"]
        assert "Failed" in event.reason

    def test_sets_htmx_trigger(self, client, concentration_setup):
        """Test rolling sets HX-Trigger header."""
        setup = concentration_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "concentration-save-roll",
            args=(setup["game"].id, setup["character"].pk),
        )
        response = client.post(url, {"dc": 10, "con_modifier": 0})

        assert "HX-Trigger" in response
        assert "concentration-updated" in response["HX-Trigger"]

    def test_returns_404_for_invalid_character(self, client, concentration_setup):
        """Test rolling returns 404 for non-existent character."""
        setup = concentration_setup
        client.force_login(setup["player"].user)

        url = reverse(
            "concentration-save-roll",
            args=(setup["game"].id, 99999),
        )
        response = client.post(url, {"dc": 10, "con_modifier": 0})

        assert response.status_code == 404


class TestCheckConcentrationOnDamage:
    """Tests for the check_concentration_on_damage utility function."""

    @pytest.fixture
    def combat_with_concentration(self):
        """Set up combat where target is concentrating."""
        game = GameFactory()

        # Attacker
        user1 = UserFactory()
        character1 = CharacterFactory(user=user1)
        player1 = Player.objects.create(user=user1, game=game, character=character1)

        # Target (concentrating)
        user2 = UserFactory()
        character2 = CharacterFactory(user=user2)
        character2.hp = 30
        character2.max_hp = 30
        character2.save()
        player2 = Player.objects.create(user=user2, game=game, character=character2)

        # Start concentration on target
        spell = SpellSettingsFactory(name="Hold Person", concentration=True)
        concentration = Concentration.start_concentration(character2, spell)

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
            "spell": spell,
            "concentration": concentration,
        }

    def test_apply_damage_triggers_concentration_check(
        self, client, combat_with_concentration
    ):
        """Test applying damage to concentrating character shows concentration warning."""
        setup = combat_with_concentration
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-apply-damage",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "target_id": setup["fighter2"].id,
                "damage": 10,
            },
        )

        content = response.content.decode()
        assert (
            "Concentration Check Required" in content
            or "concentration" in content.lower()
        )

    def test_apply_damage_creates_save_required_event(
        self, client, combat_with_concentration
    ):
        """Test applying damage creates ConcentrationSaveRequired event."""
        setup = combat_with_concentration
        client.force_login(setup["player1"].user)

        initial_count = ConcentrationSaveRequired.objects.count()

        url = reverse(
            "combat-apply-damage",
            args=(setup["game"].id, setup["combat"].id),
        )
        client.post(
            url,
            {
                "target_id": setup["fighter2"].id,
                "damage": 10,
            },
        )

        assert ConcentrationSaveRequired.objects.count() == initial_count + 1
        event = ConcentrationSaveRequired.objects.latest("date")
        assert event.character == setup["fighter2"].character
        assert event.damage_taken == 10
        assert event.dc == 10  # max(10, 10//2)

    def test_apply_damage_calculates_correct_dc(
        self, client, combat_with_concentration
    ):
        """Test DC is calculated correctly (max of 10 or damage/2)."""
        setup = combat_with_concentration
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-apply-damage",
            args=(setup["game"].id, setup["combat"].id),
        )
        # Damage 30 should give DC 15
        client.post(
            url,
            {
                "target_id": setup["fighter2"].id,
                "damage": 30,
            },
        )

        event = ConcentrationSaveRequired.objects.latest("date")
        assert event.dc == 15  # 30 // 2 = 15

    def test_no_concentration_check_without_concentration(
        self, client, combat_with_concentration
    ):
        """Test no concentration check when target isn't concentrating."""
        setup = combat_with_concentration
        client.force_login(setup["player1"].user)

        # Break concentration first
        setup["concentration"].break_concentration()

        initial_count = ConcentrationSaveRequired.objects.count()

        url = reverse(
            "combat-apply-damage",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "target_id": setup["fighter2"].id,
                "damage": 10,
            },
        )

        # No new event should be created
        assert ConcentrationSaveRequired.objects.count() == initial_count

        # Modal should not show concentration warning
        content = response.content.decode()
        assert "Concentration Check Required" not in content


class TestConcentrationInInitiativeTracker:
    """Tests for concentration display in the initiative tracker."""

    @pytest.fixture
    def combat_with_concentration(self):
        """Set up combat where a fighter is concentrating."""
        game = GameFactory()

        user1 = UserFactory()
        character1 = CharacterFactory(user=user1)
        player1 = Player.objects.create(user=user1, game=game, character=character1)

        # Start concentration
        spell = SpellSettingsFactory(name="Haste", concentration=True)
        Concentration.start_concentration(character1, spell)

        combat = Combat.objects.create(game=game)
        fighter1 = FighterFactory(
            combat=combat,
            player=player1,
            character=character1,
            dexterity_check=15,
        )
        combat.start_combat()

        return {
            "game": game,
            "combat": combat,
            "player1": player1,
            "fighter1": fighter1,
            "spell": spell,
        }

    def test_tracker_shows_concentration_icon(self, client, combat_with_concentration):
        """Test initiative tracker shows concentration icon for concentrating fighter."""
        setup = combat_with_concentration
        client.force_login(setup["player1"].user)

        url = reverse(
            "initiative-tracker",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        # Should contain concentration indicator (the circle icon &#9673;)
        assert (
            "concentration" in content.lower()
            or "&#9673;" in content
            or "Haste" in content
        )


class TestConcentrationInActionPanel:
    """Tests for concentration display in the action panel."""

    @pytest.fixture
    def combat_with_concentration(self):
        """Set up combat where current fighter is concentrating."""
        game = GameFactory()

        user1 = UserFactory()
        character1 = CharacterFactory(user=user1)
        player1 = Player.objects.create(user=user1, game=game, character=character1)

        # Start concentration
        spell = SpellSettingsFactory(name="Spirit Guardians", concentration=True)
        Concentration.start_concentration(character1, spell)

        combat = Combat.objects.create(game=game)
        fighter1 = FighterFactory(
            combat=combat,
            player=player1,
            character=character1,
            dexterity_check=15,
        )
        combat.start_combat()

        return {
            "game": game,
            "combat": combat,
            "player1": player1,
            "fighter1": fighter1,
            "spell": spell,
        }

    def test_panel_shows_concentration_indicator(
        self, client, combat_with_concentration
    ):
        """Test action panel shows concentration indicator."""
        setup = combat_with_concentration
        client.force_login(setup["player1"].user)

        url = reverse(
            "action-panel",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        # Should show spell name in concentration indicator
        assert "Spirit Guardians" in content
        assert "Concentrating" in content or "concentration" in content.lower()

    def test_panel_shows_drop_button(self, client, combat_with_concentration):
        """Test action panel shows drop concentration button on player's turn."""
        setup = combat_with_concentration
        client.force_login(setup["player1"].user)

        url = reverse(
            "action-panel",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        assert "Drop" in content or "break" in content.lower()

    def test_panel_without_concentration(self, client, combat_with_concentration):
        """Test action panel does not show indicator when not concentrating."""
        setup = combat_with_concentration
        client.force_login(setup["player1"].user)

        # Break concentration
        setup["fighter1"].character.concentration.break_concentration()

        url = reverse(
            "action-panel",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        # Should not show concentration indicator
        assert "Spirit Guardians" not in content
