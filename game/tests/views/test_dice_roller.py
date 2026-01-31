"""Tests for the dice roller views."""

from unittest.mock import patch

import pytest
from django.urls import reverse

from game.models.events import DiceRoll
from game.models.game import Player
from character.tests.factories import CharacterFactory
from user.tests.factories import UserFactory

from ..factories import GameFactory


pytestmark = pytest.mark.django_db


class TestDiceRollerModalView:
    """Tests for DiceRollerModalView."""

    @pytest.fixture
    def game_with_player(self):
        """Set up a game with a player."""
        game = GameFactory()
        user = UserFactory()
        character = CharacterFactory(user=user)
        player = Player.objects.create(user=user, game=game, character=character)
        return {"game": game, "player": player}

    def test_modal_returns_html(self, client, game_with_player):
        """Test dice roller modal returns HTML content."""
        setup = game_with_player
        client.force_login(setup["player"].user)

        url = reverse("dice-roller-modal", args=(setup["game"].id,))
        response = client.get(url)

        assert response.status_code == 200
        assert "dice-roller-modal" in response.content.decode()

    def test_modal_shows_dice_type_selector(self, client, game_with_player):
        """Test modal displays dice type selector."""
        setup = game_with_player
        client.force_login(setup["player"].user)

        url = reverse("dice-roller-modal", args=(setup["game"].id,))
        response = client.get(url)

        content = response.content.decode()
        assert "d4" in content
        assert "d6" in content
        assert "d8" in content
        assert "d10" in content
        assert "d12" in content
        assert "d20" in content

    def test_modal_shows_dice_count_input(self, client, game_with_player):
        """Test modal displays number of dice input."""
        setup = game_with_player
        client.force_login(setup["player"].user)

        url = reverse("dice-roller-modal", args=(setup["game"].id,))
        response = client.get(url)

        content = response.content.decode()
        assert "Number of Dice" in content
        assert 'name="num_dice"' in content

    def test_modal_shows_modifier_input(self, client, game_with_player):
        """Test modal displays modifier input."""
        setup = game_with_player
        client.force_login(setup["player"].user)

        url = reverse("dice-roller-modal", args=(setup["game"].id,))
        response = client.get(url)

        content = response.content.decode()
        assert "Modifier" in content
        assert 'name="modifier"' in content

    def test_modal_shows_purpose_input(self, client, game_with_player):
        """Test modal displays optional purpose input."""
        setup = game_with_player
        client.force_login(setup["player"].user)

        url = reverse("dice-roller-modal", args=(setup["game"].id,))
        response = client.get(url)

        content = response.content.decode()
        assert "Purpose" in content
        assert 'name="roll_purpose"' in content

    def test_modal_accessible_by_master(self, client):
        """Test dice roller modal accessible by game master."""
        game = GameFactory()
        client.force_login(game.master.user)

        url = reverse("dice-roller-modal", args=(game.id,))
        response = client.get(url)

        assert response.status_code == 200

    def test_modal_forbidden_for_non_participant(self, client, game_with_player):
        """Test dice roller modal forbidden for non-participants."""
        setup = game_with_player
        other_user = UserFactory()
        client.force_login(other_user)

        url = reverse("dice-roller-modal", args=(setup["game"].id,))
        response = client.get(url)

        assert response.status_code == 403


class TestDiceRollView:
    """Tests for DiceRollView."""

    @pytest.fixture
    def game_with_player(self):
        """Set up a game with a player."""
        game = GameFactory()
        user = UserFactory()
        character = CharacterFactory(user=user)
        player = Player.objects.create(user=user, game=game, character=character)
        return {"game": game, "player": player}

    def test_roll_returns_result_html(self, client, game_with_player):
        """Test dice roll returns result HTML."""
        setup = game_with_player
        client.force_login(setup["player"].user)

        url = reverse("dice-roll", args=(setup["game"].id,))
        with patch("game.services.send_to_channel"):
            response = client.post(
                url,
                {
                    "dice_type": 20,
                    "num_dice": 1,
                    "modifier": 0,
                    "roll_purpose": "",
                },
            )

        assert response.status_code == 200
        content = response.content.decode()
        assert "dice-roller-modal" in content
        assert "roll-result" in content or "total-result" in content

    @patch("utils.dice.random.randint")
    def test_roll_shows_individual_dice(self, mock_randint, client, game_with_player):
        """Test roll shows individual dice values."""
        mock_randint.side_effect = [4, 3, 6]  # Three d6 rolls
        setup = game_with_player
        client.force_login(setup["player"].user)

        url = reverse("dice-roll", args=(setup["game"].id,))
        with patch("game.services.send_to_channel"):
            response = client.post(
                url,
                {
                    "dice_type": 6,
                    "num_dice": 3,
                    "modifier": 0,
                    "roll_purpose": "",
                },
            )

        content = response.content.decode()
        assert "die-result" in content
        # Should show the individual values
        assert ">4<" in content or "4</span>" in content
        assert ">3<" in content or "3</span>" in content
        assert ">6<" in content or "6</span>" in content

    @patch("utils.dice.random.randint")
    def test_roll_calculates_total_with_modifier(
        self, mock_randint, client, game_with_player
    ):
        """Test roll calculates correct total with modifier."""
        mock_randint.return_value = 10  # Roll a 10
        setup = game_with_player
        client.force_login(setup["player"].user)

        url = reverse("dice-roll", args=(setup["game"].id,))
        with patch("game.services.send_to_channel"):
            response = client.post(
                url,
                {
                    "dice_type": 20,
                    "num_dice": 1,
                    "modifier": 5,
                    "roll_purpose": "",
                },
            )

        content = response.content.decode()
        # Total should be 10 + 5 = 15
        assert "15" in content

    def test_roll_shows_purpose(self, client, game_with_player):
        """Test roll displays purpose when provided."""
        setup = game_with_player
        client.force_login(setup["player"].user)

        url = reverse("dice-roll", args=(setup["game"].id,))
        with patch("game.services.send_to_channel"):
            response = client.post(
                url,
                {
                    "dice_type": 20,
                    "num_dice": 1,
                    "modifier": 0,
                    "roll_purpose": "Perception check",
                },
            )

        content = response.content.decode()
        assert "Perception check" in content

    def test_roll_creates_event(self, client, game_with_player):
        """Test dice roll creates DiceRoll event."""
        setup = game_with_player
        client.force_login(setup["player"].user)

        url = reverse("dice-roll", args=(setup["game"].id,))
        with patch("game.services.send_to_channel"):
            client.post(
                url,
                {
                    "dice_type": 6,
                    "num_dice": 2,
                    "modifier": 3,
                    "roll_purpose": "Damage roll",
                },
            )

        # Check event was created
        event = DiceRoll.objects.filter(game=setup["game"]).first()
        assert event is not None
        assert event.dice_notation == "2d6"
        assert event.dice_type == 6
        assert event.num_dice == 2
        assert event.modifier == 3
        assert event.roll_purpose == "Damage roll"

    def test_roll_broadcasts_to_channel(self, client, game_with_player):
        """Test dice roll broadcasts via WebSocket."""
        setup = game_with_player
        client.force_login(setup["player"].user)

        url = reverse("dice-roll", args=(setup["game"].id,))
        with patch("game.services.send_to_channel") as mock_send:
            client.post(
                url,
                {
                    "dice_type": 20,
                    "num_dice": 1,
                    "modifier": 0,
                    "roll_purpose": "",
                },
            )

        mock_send.assert_called_once()

    def test_roll_clamps_num_dice(self, client, game_with_player):
        """Test num_dice is clamped between 1 and 10."""
        setup = game_with_player
        client.force_login(setup["player"].user)

        url = reverse("dice-roll", args=(setup["game"].id,))
        with patch("game.services.send_to_channel"):
            client.post(
                url,
                {
                    "dice_type": 6,
                    "num_dice": 100,  # Over limit
                    "modifier": 0,
                    "roll_purpose": "",
                },
            )

        event = DiceRoll.objects.filter(game=setup["game"]).first()
        assert event.num_dice == 10  # Clamped to max

    def test_roll_clamps_modifier(self, client, game_with_player):
        """Test modifier is clamped between -20 and 20."""
        setup = game_with_player
        client.force_login(setup["player"].user)

        url = reverse("dice-roll", args=(setup["game"].id,))
        with patch("game.services.send_to_channel"):
            client.post(
                url,
                {
                    "dice_type": 6,
                    "num_dice": 1,
                    "modifier": 100,  # Over limit
                    "roll_purpose": "",
                },
            )

        event = DiceRoll.objects.filter(game=setup["game"]).first()
        assert event.modifier == 20  # Clamped to max

    def test_roll_accessible_by_master(self, client):
        """Test dice roll accessible by game master."""
        game = GameFactory()
        client.force_login(game.master.user)

        url = reverse("dice-roll", args=(game.id,))
        with patch("game.services.send_to_channel"):
            response = client.post(
                url,
                {
                    "dice_type": 20,
                    "num_dice": 1,
                    "modifier": 0,
                    "roll_purpose": "",
                },
            )

        assert response.status_code == 200

    def test_roll_forbidden_for_non_participant(self, client, game_with_player):
        """Test dice roll forbidden for non-participants."""
        setup = game_with_player
        other_user = UserFactory()
        client.force_login(other_user)

        url = reverse("dice-roll", args=(setup["game"].id,))
        response = client.post(
            url,
            {
                "dice_type": 20,
                "num_dice": 1,
                "modifier": 0,
                "roll_purpose": "",
            },
        )

        assert response.status_code == 403

    @patch("utils.dice.random.randint")
    def test_max_roll_highlighted(self, mock_randint, client, game_with_player):
        """Test max roll on die gets special styling."""
        mock_randint.return_value = 6  # Max on d6
        setup = game_with_player
        client.force_login(setup["player"].user)

        url = reverse("dice-roll", args=(setup["game"].id,))
        with patch("game.services.send_to_channel"):
            response = client.post(
                url,
                {
                    "dice_type": 6,
                    "num_dice": 1,
                    "modifier": 0,
                    "roll_purpose": "",
                },
            )

        content = response.content.decode()
        assert "max-roll" in content

    @patch("utils.dice.random.randint")
    def test_min_roll_highlighted(self, mock_randint, client, game_with_player):
        """Test min roll (1) on die gets special styling."""
        mock_randint.return_value = 1  # Min roll
        setup = game_with_player
        client.force_login(setup["player"].user)

        url = reverse("dice-roll", args=(setup["game"].id,))
        with patch("game.services.send_to_channel"):
            response = client.post(
                url,
                {
                    "dice_type": 20,
                    "num_dice": 1,
                    "modifier": 0,
                    "roll_purpose": "",
                },
            )

        content = response.content.decode()
        assert "min-roll" in content
