"""Tests for the attack resolution system."""

from unittest.mock import patch

import pytest

from character.constants.abilities import AbilityName
from character.constants.equipment import WeaponName, WeaponType
from character.models.equipment import Weapon, WeaponSettings
from character.models.proficiencies import WeaponProficiency
from character.tests.factories import CharacterFactory

from game.attack import (
    apply_damage,
    get_attack_ability,
    is_proficient_with_weapon,
    resolve_attack,
)

pytestmark = pytest.mark.django_db


class TestGetAttackAbility:
    """Tests for determining which ability to use for attacks."""

    @pytest.fixture
    def melee_weapon(self):
        """Create a simple melee weapon (uses STR)."""
        settings = WeaponSettings.objects.create(
            name=WeaponName.LONGSWORD,
            weapon_type=WeaponType.MARTIAL_MELEE,
            cost=15,
            damage="1d8",
            weight=3,
            properties="versatile",
        )
        return Weapon.objects.create(settings=settings)

    @pytest.fixture
    def ranged_weapon(self):
        """Create a ranged weapon (uses DEX)."""
        settings = WeaponSettings.objects.create(
            name=WeaponName.LONGBOW,
            weapon_type=WeaponType.MARTIAL_RANGED,
            cost=50,
            damage="1d8",
            weight=2,
            properties="ammunition,heavy,two_handed",
        )
        return Weapon.objects.create(settings=settings)

    @pytest.fixture
    def finesse_weapon(self):
        """Create a finesse weapon (uses STR or DEX, whichever is higher)."""
        settings = WeaponSettings.objects.create(
            name=WeaponName.RAPIER,
            weapon_type=WeaponType.MARTIAL_MELEE,
            cost=25,
            damage="1d8",
            weight=2,
            properties="finesse",
        )
        return Weapon.objects.create(settings=settings)

    @pytest.fixture
    def character_str_higher(self):
        """Create a character with higher STR than DEX."""
        character = CharacterFactory()
        # Set specific ability scores
        str_ability = character.abilities.get(ability_type__name=AbilityName.STRENGTH)
        str_ability.score = 16
        str_ability.modifier = 3
        str_ability.save()

        dex_ability = character.abilities.get(ability_type__name=AbilityName.DEXTERITY)
        dex_ability.score = 12
        dex_ability.modifier = 1
        dex_ability.save()

        return character

    @pytest.fixture
    def character_dex_higher(self):
        """Create a character with higher DEX than STR."""
        character = CharacterFactory()
        # Set specific ability scores
        str_ability = character.abilities.get(ability_type__name=AbilityName.STRENGTH)
        str_ability.score = 10
        str_ability.modifier = 0
        str_ability.save()

        dex_ability = character.abilities.get(ability_type__name=AbilityName.DEXTERITY)
        dex_ability.score = 18
        dex_ability.modifier = 4
        dex_ability.save()

        return character

    def test_melee_weapon_uses_strength(self, melee_weapon, character_str_higher):
        """Test that melee weapons use Strength."""
        ability = get_attack_ability(melee_weapon, character_str_higher)
        assert ability == str(AbilityName.STRENGTH)

    def test_ranged_weapon_uses_dexterity(self, ranged_weapon, character_str_higher):
        """Test that ranged weapons use Dexterity."""
        ability = get_attack_ability(ranged_weapon, character_str_higher)
        assert ability == str(AbilityName.DEXTERITY)

    def test_finesse_weapon_uses_higher_str(self, finesse_weapon, character_str_higher):
        """Test that finesse weapons use STR when it's higher."""
        ability = get_attack_ability(finesse_weapon, character_str_higher)
        assert ability == str(AbilityName.STRENGTH)

    def test_finesse_weapon_uses_higher_dex(self, finesse_weapon, character_dex_higher):
        """Test that finesse weapons use DEX when it's higher."""
        ability = get_attack_ability(finesse_weapon, character_dex_higher)
        assert ability == str(AbilityName.DEXTERITY)


class TestIsProficientWithWeapon:
    """Tests for weapon proficiency checks."""

    @pytest.fixture
    def weapon(self):
        """Create a weapon for testing."""
        settings = WeaponSettings.objects.create(
            name=WeaponName.SHORTSWORD,
            weapon_type=WeaponType.MARTIAL_MELEE,
            cost=10,
            damage="1d6",
            weight=2,
            properties="finesse,light",
        )
        return Weapon.objects.create(settings=settings)

    @pytest.fixture
    def character(self):
        """Create a character for testing."""
        return CharacterFactory()

    def test_not_proficient(self, character, weapon):
        """Test that character without proficiency returns False."""
        assert is_proficient_with_weapon(character, weapon) is False

    def test_is_proficient(self, character, weapon):
        """Test that character with proficiency returns True."""
        WeaponProficiency.objects.create(character=character, weapon=weapon.settings)
        assert is_proficient_with_weapon(character, weapon) is True


class TestResolveAttack:
    """Tests for the main attack resolution function."""

    @pytest.fixture
    def weapon(self):
        """Create a weapon for testing."""
        settings = WeaponSettings.objects.create(
            name=WeaponName.DAGGER,
            weapon_type=WeaponType.SIMPLE_MELEE,
            cost=2,
            damage="1d4",
            weight=1,
            properties="finesse,light,thrown",
        )
        return Weapon.objects.create(settings=settings)

    @pytest.fixture
    def attacker(self):
        """Create an attacker character."""
        character = CharacterFactory()
        character.level = 5  # Proficiency bonus of +3

        str_ability = character.abilities.get(ability_type__name=AbilityName.STRENGTH)
        str_ability.score = 14
        str_ability.modifier = 2
        str_ability.save()

        dex_ability = character.abilities.get(ability_type__name=AbilityName.DEXTERITY)
        dex_ability.score = 16
        dex_ability.modifier = 3
        dex_ability.save()

        character.save()
        return character

    @pytest.fixture
    def target(self):
        """Create a target character."""
        character = CharacterFactory()
        character.ac = 15
        character.hp = 30
        character.max_hp = 30
        character.save()
        return character

    def test_attack_miss(self, attacker, target, weapon):
        """Test that a low roll results in a miss."""
        # Mock roll_d20_test to return a low roll
        with patch("game.attack.roll_d20_test") as mock_roll:
            mock_roll.return_value = (8, False, False)  # Total 8, no nat 20/1

            result = resolve_attack(attacker, target, weapon)

            assert result.is_hit is False
            assert result.is_critical_hit is False
            assert result.is_critical_miss is False
            assert result.damage == 0
            assert result.attack_roll == 8
            assert result.target_ac == 15

    def test_attack_hit(self, attacker, target, weapon):
        """Test that a high roll results in a hit."""
        with patch("game.attack.roll_d20_test") as mock_roll:
            mock_roll.return_value = (18, False, False)  # Total 18, no nat 20/1

            with patch("game.attack.DiceString.roll_damage") as mock_damage:
                mock_damage.return_value = 3  # Rolled 3 on 1d4

                result = resolve_attack(attacker, target, weapon)

                assert result.is_hit is True
                assert result.is_critical_hit is False
                # Damage = 3 (dice) + 3 (DEX mod for finesse) = 6
                assert result.damage == 6

    def test_critical_hit_on_natural_20(self, attacker, target, weapon):
        """Test that a natural 20 is a critical hit."""
        with patch("game.attack.roll_d20_test") as mock_roll:
            # Natural 20 + modifier = 23, is_nat_20=True
            mock_roll.return_value = (23, True, False)

            with patch("game.attack.DiceString.roll_damage") as mock_damage:
                mock_damage.return_value = 6  # Rolled on doubled dice

                result = resolve_attack(attacker, target, weapon)

                assert result.is_hit is True
                assert result.is_critical_hit is True
                assert result.is_critical_miss is False
                # Damage dice should be rolled with critical=True
                mock_damage.assert_called_once_with(critical=True)
                # Damage = 6 (doubled dice) + 3 (DEX mod) = 9
                assert result.damage == 9

    def test_critical_miss_on_natural_1(self, attacker, target, weapon):
        """Test that a natural 1 always misses."""
        with patch("game.attack.roll_d20_test") as mock_roll:
            # Even with high modifier, natural 1 misses
            mock_roll.return_value = (4, False, True)  # 1 + 3 = 4, is_nat_1=True

            result = resolve_attack(attacker, target, weapon)

            assert result.is_hit is False
            assert result.is_critical_miss is True
            assert result.is_critical_hit is False
            assert result.damage == 0

    def test_critical_hit_always_hits_high_ac(self, attacker, target, weapon):
        """Test that natural 20 hits even against very high AC."""
        target.ac = 30  # Very high AC
        target.save()

        with patch("game.attack.roll_d20_test") as mock_roll:
            mock_roll.return_value = (23, True, False)  # Natural 20

            with patch("game.attack.DiceString.roll_damage") as mock_damage:
                mock_damage.return_value = 4

                result = resolve_attack(attacker, target, weapon)

                assert result.is_hit is True
                assert result.is_critical_hit is True

    def test_proficiency_bonus_added(self, attacker, target, weapon):
        """Test that proficiency bonus is added when proficient."""
        WeaponProficiency.objects.create(character=attacker, weapon=weapon.settings)

        with patch("game.attack.roll_d20_test") as mock_roll:
            mock_roll.return_value = (15, False, False)

            with patch("game.attack.DiceString.roll_damage") as mock_damage:
                mock_damage.return_value = 2

                result = resolve_attack(attacker, target, weapon)

                # Level 5 = +3 proficiency, DEX mod = +3, total modifier = +6
                assert result.attack_modifier == 6
                mock_roll.assert_called_once_with(
                    modifier=6, advantage=False, disadvantage=False
                )

    def test_no_proficiency_bonus_when_not_proficient(self, attacker, target, weapon):
        """Test that proficiency bonus is not added when not proficient."""
        with patch("game.attack.roll_d20_test") as mock_roll:
            mock_roll.return_value = (15, False, False)

            with patch("game.attack.DiceString.roll_damage") as mock_damage:
                mock_damage.return_value = 2

                result = resolve_attack(attacker, target, weapon)

                # Only DEX mod = +3, no proficiency
                assert result.attack_modifier == 3
                mock_roll.assert_called_once_with(
                    modifier=3, advantage=False, disadvantage=False
                )

    def test_advantage_passed_to_roll(self, attacker, target, weapon):
        """Test that advantage is passed to the roll function."""
        with patch("game.attack.roll_d20_test") as mock_roll:
            mock_roll.return_value = (18, False, False)

            with patch("game.attack.DiceString.roll_damage") as mock_damage:
                mock_damage.return_value = 2

                resolve_attack(attacker, target, weapon, advantage=True)

                mock_roll.assert_called_once_with(
                    modifier=3, advantage=True, disadvantage=False
                )

    def test_disadvantage_passed_to_roll(self, attacker, target, weapon):
        """Test that disadvantage is passed to the roll function."""
        with patch("game.attack.roll_d20_test") as mock_roll:
            mock_roll.return_value = (10, False, False)

            resolve_attack(attacker, target, weapon, disadvantage=True)

            mock_roll.assert_called_once_with(
                modifier=3, advantage=False, disadvantage=True
            )

    def test_attack_result_metadata(self, attacker, target, weapon):
        """Test that attack result contains correct metadata."""
        with patch("game.attack.roll_d20_test") as mock_roll:
            mock_roll.return_value = (18, False, False)

            with patch("game.attack.DiceString.roll_damage") as mock_damage:
                mock_damage.return_value = 3

                result = resolve_attack(attacker, target, weapon)

                assert result.attacker_name == attacker.name
                assert result.target_name == target.name
                assert result.weapon_name == str(weapon.settings.name)
                assert result.ability_used == str(AbilityName.DEXTERITY)  # Finesse
                assert result.damage_dice == "1d4"

    def test_damage_minimum_zero(self, attacker, target, weapon):
        """Test that damage cannot go below zero with negative modifiers."""
        # Give attacker negative modifier
        dex_ability = attacker.abilities.get(ability_type__name=AbilityName.DEXTERITY)
        dex_ability.score = 6
        dex_ability.modifier = -2
        dex_ability.save()

        str_ability = attacker.abilities.get(ability_type__name=AbilityName.STRENGTH)
        str_ability.score = 6
        str_ability.modifier = -2
        str_ability.save()

        with patch("game.attack.roll_d20_test") as mock_roll:
            mock_roll.return_value = (15, False, False)

            with patch("game.attack.DiceString.roll_damage") as mock_damage:
                mock_damage.return_value = 1  # Rolled 1 on 1d4

                result = resolve_attack(attacker, target, weapon)

                # 1 (dice) + (-2) (DEX mod) = -1, but minimum is 0
                assert result.damage == 0


class TestApplyDamage:
    """Tests for applying damage to characters."""

    @pytest.fixture
    def target(self):
        """Create a target character."""
        character = CharacterFactory()
        character.hp = 20
        character.max_hp = 20
        character.save()
        return character

    def test_apply_damage_reduces_hp(self, target):
        """Test that damage reduces target HP."""
        remaining = apply_damage(target, 8)

        target.refresh_from_db()
        assert remaining == 12
        assert target.hp == 12

    def test_apply_damage_cannot_go_negative(self, target):
        """Test that HP cannot go below 0."""
        remaining = apply_damage(target, 100)

        target.refresh_from_db()
        assert remaining == 0
        assert target.hp == 0

    def test_apply_zero_damage(self, target):
        """Test that zero damage doesn't change HP."""
        remaining = apply_damage(target, 0)

        target.refresh_from_db()
        assert remaining == 20
        assert target.hp == 20
