"""Tests for the weapon mastery system."""

from unittest.mock import patch

import pytest

from character.constants.abilities import AbilityName
from character.constants.equipment import WeaponMastery, WeaponName, WeaponType
from character.models.equipment import Weapon, WeaponSettings
from character.tests.factories import CharacterFactory

from game.attack import resolve_attack
from game.mastery import (
    get_mastery_save_dc,
    resolve_mastery,
    resolve_mastery_on_hit,
    resolve_mastery_on_miss,
)

pytestmark = pytest.mark.django_db


class TestGetMasterySaveDC:
    """Tests for mastery save DC calculation."""

    def test_save_dc_calculation(self):
        """Test DC = 8 + proficiency + ability modifier."""
        dc = get_mastery_save_dc(attacker_proficiency=2, ability_modifier=3)
        assert dc == 13  # 8 + 2 + 3

    def test_save_dc_with_high_values(self):
        """Test DC with high proficiency and modifier."""
        dc = get_mastery_save_dc(attacker_proficiency=6, ability_modifier=5)
        assert dc == 19  # 8 + 6 + 5

    def test_save_dc_with_negative_modifier(self):
        """Test DC with negative ability modifier."""
        dc = get_mastery_save_dc(attacker_proficiency=2, ability_modifier=-1)
        assert dc == 9  # 8 + 2 + (-1)


class TestResolveMasteryOnMiss:
    """Tests for mastery effects that trigger on miss."""

    def test_graze_deals_ability_modifier_damage(self):
        """Test Graze deals ability modifier damage on miss."""
        effect = resolve_mastery_on_miss(
            mastery=str(WeaponMastery.GRAZE),
            ability_modifier=3,
        )
        assert effect.triggered is True
        assert effect.graze_damage == 3
        assert "3 damage" in effect.description

    def test_graze_minimum_zero_damage(self):
        """Test Graze damage cannot go below 0."""
        effect = resolve_mastery_on_miss(
            mastery=str(WeaponMastery.GRAZE),
            ability_modifier=-2,
        )
        assert effect.triggered is True
        assert effect.graze_damage == 0

    def test_other_masteries_dont_trigger_on_miss(self):
        """Test that non-Graze masteries don't trigger on miss."""
        for mastery in [
            WeaponMastery.CLEAVE,
            WeaponMastery.PUSH,
            WeaponMastery.SAP,
            WeaponMastery.SLOW,
            WeaponMastery.TOPPLE,
            WeaponMastery.VEX,
            WeaponMastery.NICK,
        ]:
            effect = resolve_mastery_on_miss(
                mastery=str(mastery),
                ability_modifier=3,
            )
            assert effect.triggered is False

    def test_no_mastery_returns_empty_effect(self):
        """Test that no mastery returns empty effect."""
        effect = resolve_mastery_on_miss(mastery=None, ability_modifier=3)
        assert effect.triggered is False
        assert effect.mastery is None


class TestResolveMasteryOnHit:
    """Tests for mastery effects that trigger on hit."""

    def test_cleave_on_kill(self):
        """Test Cleave provides excess damage on kill."""
        effect = resolve_mastery_on_hit(
            mastery=str(WeaponMastery.CLEAVE),
            ability_modifier=3,
            attacker_proficiency=2,
            damage_dealt=15,
            target_hp_remaining=-5,  # Overkill by 5
        )
        assert effect.triggered is True
        assert effect.cleave_damage_available == 5
        assert "excess damage" in effect.description

    def test_cleave_no_kill(self):
        """Test Cleave doesn't trigger if target survives."""
        effect = resolve_mastery_on_hit(
            mastery=str(WeaponMastery.CLEAVE),
            ability_modifier=3,
            attacker_proficiency=2,
            damage_dealt=10,
            target_hp_remaining=5,  # Target still alive
        )
        assert effect.triggered is True
        assert effect.cleave_damage_available == 0

    def test_push_effect(self):
        """Test Push pushes target 10 feet."""
        effect = resolve_mastery_on_hit(
            mastery=str(WeaponMastery.PUSH),
            ability_modifier=3,
            attacker_proficiency=2,
            damage_dealt=10,
            target_hp_remaining=10,
        )
        assert effect.triggered is True
        assert effect.push_distance == 10
        assert "10 feet" in effect.description

    def test_sap_gives_disadvantage(self):
        """Test Sap gives target disadvantage on next attack."""
        effect = resolve_mastery_on_hit(
            mastery=str(WeaponMastery.SAP),
            ability_modifier=3,
            attacker_proficiency=2,
            damage_dealt=10,
            target_hp_remaining=10,
        )
        assert effect.triggered is True
        assert effect.target_has_disadvantage is True
        assert "disadvantage" in effect.description

    def test_slow_reduces_speed(self):
        """Test Slow reduces target speed by 10 feet."""
        effect = resolve_mastery_on_hit(
            mastery=str(WeaponMastery.SLOW),
            ability_modifier=3,
            attacker_proficiency=2,
            damage_dealt=10,
            target_hp_remaining=10,
        )
        assert effect.triggered is True
        assert effect.speed_reduction == 10
        assert "10 feet" in effect.description

    def test_topple_requires_save(self):
        """Test Topple sets save DC for prone."""
        effect = resolve_mastery_on_hit(
            mastery=str(WeaponMastery.TOPPLE),
            ability_modifier=3,
            attacker_proficiency=2,
            damage_dealt=10,
            target_hp_remaining=10,
        )
        assert effect.triggered is True
        assert effect.topple_save_dc == 13  # 8 + 2 + 3
        assert "DC 13" in effect.description
        assert "Constitution" in effect.description

    def test_vex_gives_advantage(self):
        """Test Vex gives attacker advantage on next attack."""
        effect = resolve_mastery_on_hit(
            mastery=str(WeaponMastery.VEX),
            ability_modifier=3,
            attacker_proficiency=2,
            damage_dealt=10,
            target_hp_remaining=10,
        )
        assert effect.triggered is True
        assert effect.attacker_has_advantage_on_next is True
        assert "advantage" in effect.description

    def test_nick_allows_extra_attack(self):
        """Test Nick allows extra attack with light weapon."""
        effect = resolve_mastery_on_hit(
            mastery=str(WeaponMastery.NICK),
            ability_modifier=3,
            attacker_proficiency=2,
            damage_dealt=10,
            target_hp_remaining=10,
        )
        assert effect.triggered is True
        assert effect.attacker_can_nick is True
        assert "extra attack" in effect.description

    def test_graze_doesnt_trigger_on_hit(self):
        """Test Graze doesn't trigger on hit."""
        effect = resolve_mastery_on_hit(
            mastery=str(WeaponMastery.GRAZE),
            ability_modifier=3,
            attacker_proficiency=2,
            damage_dealt=10,
            target_hp_remaining=10,
        )
        assert effect.triggered is False

    def test_no_mastery_returns_empty_effect(self):
        """Test that no mastery returns empty effect."""
        effect = resolve_mastery_on_hit(
            mastery=None,
            ability_modifier=3,
            attacker_proficiency=2,
            damage_dealt=10,
            target_hp_remaining=10,
        )
        assert effect.triggered is False
        assert effect.mastery is None


class TestResolveMastery:
    """Tests for the main resolve_mastery function."""

    def test_hit_delegates_to_on_hit(self):
        """Test that hits delegate to on_hit resolution."""
        effect = resolve_mastery(
            mastery=str(WeaponMastery.PUSH),
            is_hit=True,
            ability_modifier=3,
            attacker_proficiency=2,
            damage_dealt=10,
            target_hp_remaining=10,
        )
        assert effect.push_distance == 10

    def test_miss_delegates_to_on_miss(self):
        """Test that misses delegate to on_miss resolution."""
        effect = resolve_mastery(
            mastery=str(WeaponMastery.GRAZE),
            is_hit=False,
            ability_modifier=3,
            attacker_proficiency=2,
        )
        assert effect.graze_damage == 3


class TestMasteryIntegration:
    """Integration tests for mastery with attack resolution."""

    @pytest.fixture
    def graze_weapon(self):
        """Create a weapon with Graze mastery."""
        settings = WeaponSettings.objects.create(
            name=WeaponName.GREATSWORD,
            weapon_type=WeaponType.MARTIAL_MELEE,
            cost=50,
            damage="2d6",
            weight=6,
            properties="heavy,two_handed",
            mastery=WeaponMastery.GRAZE,
        )
        return Weapon.objects.create(settings=settings)

    @pytest.fixture
    def vex_weapon(self):
        """Create a weapon with Vex mastery."""
        settings = WeaponSettings.objects.create(
            name=WeaponName.LONGSWORD,
            weapon_type=WeaponType.MARTIAL_MELEE,
            cost=15,
            damage="1d8",
            weight=3,
            properties="versatile",
            mastery=WeaponMastery.VEX,
        )
        return Weapon.objects.create(settings=settings)

    @pytest.fixture
    def attacker(self):
        """Create an attacker character."""
        character = CharacterFactory()
        character.level = 5

        str_ability = character.abilities.get(ability_type__name=AbilityName.STRENGTH)
        str_ability.score = 16
        str_ability.modifier = 3
        str_ability.save()

        character.save()
        return character

    @pytest.fixture
    def target(self):
        """Create a target character."""
        character = CharacterFactory()
        character.ac = 15
        character.hp = 30
        character.save()
        return character

    def test_graze_damage_on_miss(self, attacker, target, graze_weapon):
        """Test that Graze applies damage on miss."""
        with patch("game.attack.roll_d20_test") as mock_roll:
            mock_roll.return_value = (10, False, False)  # Miss

            result = resolve_attack(attacker, target, graze_weapon, use_mastery=True)

            assert result.is_hit is False
            assert result.damage == 3  # Graze damage = ability modifier
            assert result.mastery_effect.graze_damage == 3

    def test_vex_advantage_on_hit(self, attacker, target, vex_weapon):
        """Test that Vex grants advantage on next attack."""
        with patch("game.attack.roll_d20_test") as mock_roll:
            mock_roll.return_value = (18, False, False)  # Hit

            with patch("game.attack.DiceString.roll_damage") as mock_damage:
                mock_damage.return_value = 5

                result = resolve_attack(attacker, target, vex_weapon, use_mastery=True)

                assert result.is_hit is True
                assert result.mastery_effect.attacker_has_advantage_on_next is True

    def test_mastery_not_applied_when_disabled(self, attacker, target, graze_weapon):
        """Test that mastery is not applied when use_mastery=False."""
        with patch("game.attack.roll_d20_test") as mock_roll:
            mock_roll.return_value = (10, False, False)  # Miss

            result = resolve_attack(attacker, target, graze_weapon, use_mastery=False)

            assert result.is_hit is False
            assert result.damage == 0  # No graze damage
            assert result.mastery_effect.triggered is False

    def test_mastery_not_applied_without_mastery_property(self, attacker, target):
        """Test that no mastery effect when weapon has no mastery."""
        settings = WeaponSettings.objects.create(
            name=WeaponName.HANDAXE,
            weapon_type=WeaponType.SIMPLE_MELEE,
            cost=5,
            damage="1d6",
            weight=2,
            properties="light,thrown",
            mastery=None,
        )
        weapon = Weapon.objects.create(settings=settings)

        with patch("game.attack.roll_d20_test") as mock_roll:
            mock_roll.return_value = (18, False, False)

            with patch("game.attack.DiceString.roll_damage") as mock_damage:
                mock_damage.return_value = 4

                result = resolve_attack(attacker, target, weapon, use_mastery=True)

                assert result.mastery_effect.triggered is False
