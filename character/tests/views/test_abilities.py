import pytest
from django.urls import reverse
from unittest.mock import patch

from character.ability_modifiers import compute_ability_modifier
from character.views.abilities import (
    POINT_BUY_COSTS,
    POINT_BUY_TOTAL,
    STANDARD_ARRAY,
    roll_4d6_drop_lowest,
)
from ..factories import CharacterFactory, AbilityTypeFactory


@pytest.fixture
def ability_character(client):
    """Create a test character for ability tests."""
    # Ensure all ability types exist
    for name in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
        AbilityTypeFactory(name=name)
    char = CharacterFactory()
    client.force_login(char.user)
    return char


@pytest.mark.django_db
class TestAbilityModifierComputation:
    """Test ability modifier calculation."""

    def test_modifier_for_score_8(self):
        assert compute_ability_modifier(8) == -1

    def test_modifier_for_score_10(self):
        assert compute_ability_modifier(10) == 0

    def test_modifier_for_score_11(self):
        assert compute_ability_modifier(11) == 0

    def test_modifier_for_score_12(self):
        assert compute_ability_modifier(12) == 1

    def test_modifier_for_score_15(self):
        assert compute_ability_modifier(15) == 2

    def test_modifier_for_score_18(self):
        assert compute_ability_modifier(18) == 4

    def test_modifier_for_score_20(self):
        assert compute_ability_modifier(20) == 5


@pytest.mark.django_db
class TestRoll4d6DropLowest:
    """Test the 4d6 drop lowest rolling function."""

    def test_roll_returns_tuple(self):
        result = roll_4d6_drop_lowest()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_roll_total_in_valid_range(self):
        total, _ = roll_4d6_drop_lowest()
        # Min: 3 (three 1s), Max: 18 (three 6s)
        assert 3 <= total <= 18

    def test_roll_returns_four_dice(self):
        _, dice = roll_4d6_drop_lowest()
        assert len(dice) == 4

    def test_roll_dice_in_valid_range(self):
        _, dice = roll_4d6_drop_lowest()
        for die in dice:
            assert 1 <= die <= 6

    def test_roll_dice_sorted_descending(self):
        _, dice = roll_4d6_drop_lowest()
        assert dice == sorted(dice, reverse=True)

    def test_roll_total_equals_sum_of_top_three(self):
        total, dice = roll_4d6_drop_lowest()
        assert total == sum(dice[:3])


@pytest.mark.django_db
class TestPointBuyCosts:
    """Test point buy cost constants."""

    def test_cost_for_8_is_zero(self):
        assert POINT_BUY_COSTS[8] == 0

    def test_cost_for_15_is_nine(self):
        assert POINT_BUY_COSTS[15] == 9

    def test_total_points_is_27(self):
        assert POINT_BUY_TOTAL == 27

    def test_all_scores_have_costs(self):
        for score in range(8, 16):
            assert score in POINT_BUY_COSTS


@pytest.mark.django_db
class TestStandardArray:
    """Test standard array constants."""

    def test_standard_array_has_six_values(self):
        assert len(STANDARD_ARRAY) == 6

    def test_standard_array_contains_correct_values(self):
        assert sorted(STANDARD_ARRAY, reverse=True) == [15, 14, 13, 12, 10, 8]


@pytest.mark.django_db
class TestAbilityAssignmentModalView:
    """Test the ability assignment modal view."""

    def test_modal_view_returns_200(self, client, ability_character):
        url = reverse("ability-assignment-modal", args=[ability_character.pk])
        response = client.get(url)
        assert response.status_code == 200

    def test_modal_view_contains_modal_element(self, client, ability_character):
        url = reverse("ability-assignment-modal", args=[ability_character.pk])
        response = client.get(url)
        assert b"ability-assignment-modal" in response.content

    def test_modal_view_contains_mode_tabs(self, client, ability_character):
        url = reverse("ability-assignment-modal", args=[ability_character.pk])
        response = client.get(url)
        assert b"Point Buy" in response.content
        assert b"Standard Array" in response.content
        assert b"Roll" in response.content

    def test_modal_view_contains_abilities(self, client, ability_character):
        url = reverse("ability-assignment-modal", args=[ability_character.pk])
        response = client.get(url)
        assert b"Strength" in response.content
        assert b"Dexterity" in response.content
        assert b"Constitution" in response.content
        assert b"Intelligence" in response.content
        assert b"Wisdom" in response.content
        assert b"Charisma" in response.content


@pytest.mark.django_db
class TestAbilityPointBuyView:
    """Test the point buy view."""

    def test_point_buy_view_returns_200(self, client, ability_character):
        url = reverse("ability-point-buy", args=[ability_character.pk])
        data = {
            "ability_STR": "10",
            "ability_DEX": "10",
            "ability_CON": "10",
            "ability_INT": "10",
            "ability_WIS": "10",
            "ability_CHA": "10",
        }
        response = client.post(url, data)
        assert response.status_code == 200

    def test_point_buy_calculates_points_remaining(self, client, ability_character):
        url = reverse("ability-point-buy", args=[ability_character.pk])
        # All 10s = 6 * 2 = 12 points spent, 27 - 12 = 15 remaining
        data = {
            "ability_STR": "10",
            "ability_DEX": "10",
            "ability_CON": "10",
            "ability_INT": "10",
            "ability_WIS": "10",
            "ability_CHA": "10",
        }
        response = client.post(url, data)
        assert b"15" in response.content  # Points remaining

    def test_point_buy_applies_racial_bonus(self, client, ability_character):
        url = reverse("ability-point-buy", args=[ability_character.pk])
        data = {
            "ability_STR": "15",
            "ability_DEX": "8",
            "ability_CON": "8",
            "ability_INT": "8",
            "ability_WIS": "8",
            "ability_CHA": "8",
            "racial_bonus_STR": "2",
        }
        response = client.post(url, data)
        # 15 + 2 = 17
        assert b"17" in response.content

    def test_point_buy_clamps_invalid_score(self, client, ability_character):
        url = reverse("ability-point-buy", args=[ability_character.pk])
        data = {
            "ability_STR": "20",  # Invalid, should clamp to 15
            "ability_DEX": "8",
            "ability_CON": "8",
            "ability_INT": "8",
            "ability_WIS": "8",
            "ability_CHA": "8",
        }
        response = client.post(url, data)
        assert response.status_code == 200


@pytest.mark.django_db
class TestAbilityStandardArrayView:
    """Test the standard array view."""

    def test_standard_array_view_returns_200(self, client, ability_character):
        url = reverse("ability-standard-array", args=[ability_character.pk])
        data = {
            "ability_STR": "15",
            "ability_DEX": "14",
            "ability_CON": "13",
            "ability_INT": "12",
            "ability_WIS": "10",
            "ability_CHA": "8",
        }
        response = client.post(url, data)
        assert response.status_code == 200

    def test_standard_array_accepts_valid_assignment(self, client, ability_character):
        url = reverse("ability-standard-array", args=[ability_character.pk])
        data = {
            "ability_STR": "15",
            "ability_DEX": "14",
            "ability_CON": "13",
            "ability_INT": "12",
            "ability_WIS": "10",
            "ability_CHA": "8",
        }
        response = client.post(url, data)
        # Should not contain error message about duplicates
        assert b"Each value can only be used once" not in response.content

    def test_standard_array_detects_duplicate_values(self, client, ability_character):
        url = reverse("ability-standard-array", args=[ability_character.pk])
        data = {
            "ability_STR": "15",
            "ability_DEX": "15",  # Duplicate!
            "ability_CON": "13",
            "ability_INT": "12",
            "ability_WIS": "10",
            "ability_CHA": "8",
        }
        response = client.post(url, data)
        assert b"Each value can only be used once" in response.content

    def test_standard_array_applies_racial_bonus(self, client, ability_character):
        url = reverse("ability-standard-array", args=[ability_character.pk])
        data = {
            "ability_STR": "15",
            "ability_DEX": "14",
            "ability_CON": "13",
            "ability_INT": "12",
            "ability_WIS": "10",
            "ability_CHA": "8",
            "racial_bonus_STR": "2",
        }
        response = client.post(url, data)
        # 15 + 2 = 17
        assert b"17" in response.content


@pytest.mark.django_db
class TestAbilityRollView:
    """Test the roll view."""

    def test_roll_view_returns_200(self, client, ability_character):
        url = reverse("ability-roll", args=[ability_character.pk])
        data = {"action": "roll"}
        response = client.post(url, data)
        assert response.status_code == 200

    def test_roll_view_generates_rolls(self, client, ability_character):
        url = reverse("ability-roll", args=[ability_character.pk])
        data = {"action": "roll"}
        response = client.post(url, data)
        assert b"die-face" in response.content  # Dice display elements

    def test_roll_view_shows_reroll_button(self, client, ability_character):
        url = reverse("ability-roll", args=[ability_character.pk])
        data = {"action": "roll"}
        response = client.post(url, data)
        assert b"Reroll All" in response.content

    @patch("character.views.abilities.roll_4d6_drop_lowest")
    def test_roll_view_uses_roll_function(self, mock_roll, client, ability_character):
        mock_roll.return_value = (12, [4, 4, 4, 1])
        url = reverse("ability-roll", args=[ability_character.pk])
        data = {"action": "roll"}
        response = client.post(url, data)
        assert mock_roll.called
        assert response.status_code == 200

    def test_roll_view_applies_racial_bonus(self, client, ability_character):
        url = reverse("ability-roll", args=[ability_character.pk])
        data = {
            "action": "roll",
            "racial_bonus_STR": "2",
        }
        response = client.post(url, data)
        assert response.status_code == 200


@pytest.mark.django_db
class TestAbilitySaveView:
    """Test the save view."""

    def test_save_view_returns_200(self, client, ability_character):
        url = reverse("ability-save", args=[ability_character.pk])
        data = {
            "ability_STR": "15",
            "ability_DEX": "14",
            "ability_CON": "13",
            "ability_INT": "12",
            "ability_WIS": "10",
            "ability_CHA": "8",
        }
        response = client.post(url, data)
        assert response.status_code == 200

    def test_save_view_shows_success_message(self, client, ability_character):
        url = reverse("ability-save", args=[ability_character.pk])
        data = {
            "ability_STR": "15",
            "ability_DEX": "14",
            "ability_CON": "13",
            "ability_INT": "12",
            "ability_WIS": "10",
            "ability_CHA": "8",
        }
        response = client.post(url, data)
        assert b"Abilities Saved" in response.content

    def test_save_view_updates_character_abilities(self, client, ability_character):
        url = reverse("ability-save", args=[ability_character.pk])
        data = {
            "ability_STR": "15",
            "ability_DEX": "14",
            "ability_CON": "13",
            "ability_INT": "12",
            "ability_WIS": "10",
            "ability_CHA": "8",
        }
        client.post(url, data)
        ability_character.refresh_from_db()
        assert ability_character.strength.score == 15
        assert ability_character.dexterity.score == 14
        assert ability_character.constitution.score == 13
        assert ability_character.intelligence.score == 12
        assert ability_character.wisdom.score == 10
        assert ability_character.charisma.score == 8

    def test_save_view_applies_racial_bonus(self, client, ability_character):
        url = reverse("ability-save", args=[ability_character.pk])
        data = {
            "ability_STR": "15",
            "ability_DEX": "14",
            "ability_CON": "13",
            "ability_INT": "12",
            "ability_WIS": "10",
            "ability_CHA": "8",
            "racial_bonus_STR": "2",
        }
        client.post(url, data)
        ability_character.refresh_from_db()
        # 15 + 2 = 17
        assert ability_character.strength.score == 17

    def test_save_view_calculates_modifiers(self, client, ability_character):
        url = reverse("ability-save", args=[ability_character.pk])
        data = {
            "ability_STR": "15",
            "ability_DEX": "14",
            "ability_CON": "13",
            "ability_INT": "12",
            "ability_WIS": "10",
            "ability_CHA": "8",
        }
        client.post(url, data)
        ability_character.refresh_from_db()
        assert ability_character.strength.modifier == 2  # (15-10)/2 = 2
        assert ability_character.dexterity.modifier == 2  # (14-10)/2 = 2
        assert ability_character.constitution.modifier == 1  # (13-10)/2 = 1
        assert ability_character.intelligence.modifier == 1  # (12-10)/2 = 1
        assert ability_character.wisdom.modifier == 0  # (10-10)/2 = 0
        assert ability_character.charisma.modifier == -1  # (8-10)/2 = -1

    def test_save_view_clamps_score_to_max_30(self, client, ability_character):
        url = reverse("ability-save", args=[ability_character.pk])
        data = {
            "ability_STR": "28",
            "ability_DEX": "8",
            "ability_CON": "8",
            "ability_INT": "8",
            "ability_WIS": "8",
            "ability_CHA": "8",
            "racial_bonus_STR": "4",  # Would be 32, should clamp to 30
        }
        client.post(url, data)
        ability_character.refresh_from_db()
        assert ability_character.strength.score == 30
