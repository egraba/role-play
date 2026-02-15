"""Tests for the attack resolution system."""

from unittest.mock import patch

import pytest

from character.constants.abilities import AbilityName
from equipment.constants.equipment import WeaponName, WeaponType
from equipment.models.equipment import Weapon, WeaponSettings
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
        settings, _ = WeaponSettings.objects.update_or_create(
            name=WeaponName.LONGSWORD,
            defaults={
                "weapon_type": WeaponType.MARTIAL_MELEE,
                "cost": 15,
                "damage": "1d8",
                "weight": 3,
                "properties": "versatile",
            },
        )
        return Weapon.objects.create(settings=settings)

    @pytest.fixture
    def ranged_weapon(self):
        """Create a ranged weapon (uses DEX)."""
        settings, _ = WeaponSettings.objects.update_or_create(
            name=WeaponName.LONGBOW,
            defaults={
                "weapon_type": WeaponType.MARTIAL_RANGED,
                "cost": 50,
                "damage": "1d8",
                "weight": 2,
                "properties": "ammunition,heavy,two_handed",
            },
        )
        return Weapon.objects.create(settings=settings)

    @pytest.fixture
    def finesse_weapon(self):
        """Create a finesse weapon (uses STR or DEX, whichever is higher)."""
        settings, _ = WeaponSettings.objects.update_or_create(
            name=WeaponName.RAPIER,
            defaults={
                "weapon_type": WeaponType.MARTIAL_MELEE,
                "cost": 25,
                "damage": "1d8",
                "weight": 2,
                "properties": "finesse",
            },
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


class TestGetAttackAbilityEdgeCases:
    """Additional edge case tests for ability selection."""

    @pytest.fixture
    def character_equal_str_dex(self):
        """Create a character with equal STR and DEX."""
        character = CharacterFactory()
        str_ability = character.abilities.get(ability_type__name=AbilityName.STRENGTH)
        str_ability.score = 14
        str_ability.modifier = 2
        str_ability.save()

        dex_ability = character.abilities.get(ability_type__name=AbilityName.DEXTERITY)
        dex_ability.score = 14
        dex_ability.modifier = 2
        dex_ability.save()

        return character

    @pytest.fixture
    def finesse_weapon(self):
        """Create a finesse weapon."""
        settings, _ = WeaponSettings.objects.update_or_create(
            name=WeaponName.SCIMITAR,
            defaults={
                "weapon_type": WeaponType.MARTIAL_MELEE,
                "cost": 25,
                "damage": "1d6",
                "weight": 3,
                "properties": "finesse,light",
            },
        )
        return Weapon.objects.create(settings=settings)

    @pytest.fixture
    def melee_weapon(self):
        """Create a non-finesse melee weapon."""
        settings, _ = WeaponSettings.objects.update_or_create(
            name=WeaponName.GREATAXE,
            defaults={
                "weapon_type": WeaponType.MARTIAL_MELEE,
                "cost": 30,
                "damage": "1d12",
                "weight": 7,
                "properties": "heavy,two_handed",
            },
        )
        return Weapon.objects.create(settings=settings)

    @pytest.fixture
    def character_high_dex(self):
        """Create a character with high DEX."""
        character = CharacterFactory()
        str_ability = character.abilities.get(ability_type__name=AbilityName.STRENGTH)
        str_ability.score = 10
        str_ability.modifier = 0
        str_ability.save()

        dex_ability = character.abilities.get(ability_type__name=AbilityName.DEXTERITY)
        dex_ability.score = 18
        dex_ability.modifier = 4
        dex_ability.save()

        return character

    def test_finesse_uses_dex_when_equal(self, finesse_weapon, character_equal_str_dex):
        """Test that finesse weapons prefer DEX when STR and DEX are equal."""
        ability = get_attack_ability(finesse_weapon, character_equal_str_dex)
        assert ability == str(AbilityName.DEXTERITY)

    def test_non_finesse_melee_uses_str_even_with_high_dex(
        self, melee_weapon, character_high_dex
    ):
        """Test that non-finesse melee weapons always use STR."""
        ability = get_attack_ability(melee_weapon, character_high_dex)
        assert ability == str(AbilityName.STRENGTH)

    def test_weapon_with_no_properties(self, character_high_dex):
        """Test weapon with null properties field."""
        settings, _ = WeaponSettings.objects.update_or_create(
            name=WeaponName.CLUB,
            defaults={
                "weapon_type": WeaponType.SIMPLE_MELEE,
                "cost": 1,
                "damage": "1d4",
                "weight": 2,
                "properties": None,
            },
        )
        weapon = Weapon.objects.create(settings=settings)

        ability = get_attack_ability(weapon, character_high_dex)
        assert ability == str(AbilityName.STRENGTH)


class TestIsProficientWithWeapon:
    """Tests for weapon proficiency checks."""

    @pytest.fixture
    def weapon(self):
        """Create a weapon for testing."""
        settings, _ = WeaponSettings.objects.update_or_create(
            name=WeaponName.SHORTSWORD,
            defaults={
                "weapon_type": WeaponType.MARTIAL_MELEE,
                "cost": 10,
                "damage": "1d6",
                "weight": 2,
                "properties": "finesse,light",
            },
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
        settings, _ = WeaponSettings.objects.update_or_create(
            name=WeaponName.DAGGER,
            defaults={
                "weapon_type": WeaponType.SIMPLE_MELEE,
                "cost": 2,
                "damage": "1d4",
                "weight": 1,
                "properties": "finesse,light,thrown",
            },
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
        # Natural roll of 5, + modifier 3 = 8, misses AC 15
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.return_value = (5, [5])

            result = resolve_attack(attacker, target, weapon)

            assert result.is_hit is False
            assert result.is_critical_hit is False
            assert result.is_critical_miss is False
            assert result.damage == 0
            assert result.attack_roll == 8  # 5 + 3
            assert result.target_ac == 15
            assert result.damage_rolls == []

    def test_attack_hit(self, attacker, target, weapon):
        """Test that a high roll results in a hit."""
        # Natural 15 + modifier 3 = 18, hits AC 15; then damage roll of [3]
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.side_effect = [(15, [15]), (3, [3])]

            result = resolve_attack(attacker, target, weapon)

            assert result.is_hit is True
            assert result.is_critical_hit is False
            # Damage = 3 (dice) + 3 (DEX mod for finesse) = 6
            assert result.damage == 6
            assert result.damage_rolls == [3]

    def test_critical_hit_on_natural_20(self, attacker, target, weapon):
        """Test that a natural 20 is a critical hit."""
        # Natural 20 for d20, then two damage rolls (normal + crit)
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.side_effect = [(20, [20]), (3, [3]), (3, [3])]

            result = resolve_attack(attacker, target, weapon)

            assert result.is_hit is True
            assert result.is_critical_hit is True
            assert result.is_critical_miss is False
            # Damage = 3 + 3 (doubled dice) + 3 (DEX mod) = 9
            assert result.damage == 9
            assert result.damage_rolls == [3, 3]

    def test_critical_miss_on_natural_1(self, attacker, target, weapon):
        """Test that a natural 1 always misses."""
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.return_value = (1, [1])

            result = resolve_attack(attacker, target, weapon)

            assert result.is_hit is False
            assert result.is_critical_miss is True
            assert result.is_critical_hit is False
            assert result.damage == 0
            assert result.damage_rolls == []

    def test_critical_hit_always_hits_high_ac(self, attacker, target, weapon):
        """Test that natural 20 hits even against very high AC."""
        target.ac = 30  # Very high AC
        target.save()

        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.side_effect = [(20, [20]), (4, [4]), (4, [4])]

            result = resolve_attack(attacker, target, weapon)

            assert result.is_hit is True
            assert result.is_critical_hit is True

    def test_proficiency_bonus_added(self, attacker, target, weapon):
        """Test that proficiency bonus is added when proficient."""
        WeaponProficiency.objects.create(character=attacker, weapon=weapon.settings)

        # Natural 9 + modifier 6 (3 DEX + 3 prof) = 15, hits AC 15
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.side_effect = [(9, [9]), (2, [2])]

            result = resolve_attack(attacker, target, weapon)

            # Level 5 = +3 proficiency, DEX mod = +3, total modifier = +6
            assert result.attack_modifier == 6
            assert result.attack_roll == 15  # 9 + 6

    def test_no_proficiency_bonus_when_not_proficient(self, attacker, target, weapon):
        """Test that proficiency bonus is not added when not proficient."""
        # Natural 12 + modifier 3 = 15, hits AC 15
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.side_effect = [(12, [12]), (2, [2])]

            result = resolve_attack(attacker, target, weapon)

            # Only DEX mod = +3, no proficiency
            assert result.attack_modifier == 3
            assert result.attack_roll == 15  # 12 + 3

    def test_advantage_uses_roll_with_advantage(self, attacker, target, weapon):
        """Test that advantage uses roll_with_advantage."""
        with patch("game.attack.DiceString.roll_with_advantage") as mock_adv:
            mock_adv.return_value = (18, 18, 5)  # best=18, roll1=18, roll2=5

            with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
                mock_roll.return_value = (2, [2])  # damage roll

                result = resolve_attack(attacker, target, weapon, advantage=True)

                mock_adv.assert_called_once()
                assert result.natural_roll == 18
                assert result.second_natural_roll == 5

    def test_disadvantage_uses_roll_with_disadvantage(self, attacker, target, weapon):
        """Test that disadvantage uses roll_with_disadvantage."""
        with patch("game.attack.DiceString.roll_with_disadvantage") as mock_dis:
            mock_dis.return_value = (5, 5, 18)  # worst=5, roll1=5, roll2=18

            resolve_attack(attacker, target, weapon, disadvantage=True)

            mock_dis.assert_called_once()

    def test_attack_result_metadata(self, attacker, target, weapon):
        """Test that attack result contains correct metadata."""
        # Natural 15 + modifier 3 = 18, hits AC 15
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.side_effect = [(15, [15]), (3, [3])]

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

        # Natural 17 + modifier (-2) = 15, hits AC 15; damage [1]
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.side_effect = [(17, [17]), (1, [1])]

            result = resolve_attack(attacker, target, weapon)

            # 1 (dice) + (-2) (DEX mod) = -1, but minimum is 0
            assert result.damage == 0

    def test_attack_result_includes_damage_rolls(self, attacker, target, weapon):
        """Test that AttackResult includes individual damage die values on hit."""
        # Natural 15 + modifier 3 = 18, hits AC 15; damage [4]
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.side_effect = [(15, [15]), (4, [4])]

            result = resolve_attack(attacker, target, weapon)

            assert result.is_hit is True
            assert isinstance(result.damage_rolls, list)
            assert len(result.damage_rolls) > 0
            assert result.damage_rolls == [4]

    def test_attack_miss_has_empty_damage_rolls(self, attacker, target, weapon):
        """Test that a miss has empty damage_rolls."""
        # Natural 1, always misses
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.return_value = (1, [1])

            result = resolve_attack(attacker, target, weapon)

            assert result.is_hit is False
            assert result.damage_rolls == []

    def test_advantage_populates_second_natural_roll(self, attacker, target, weapon):
        """Test that advantage populates second_natural_roll with discarded roll."""
        with patch("game.attack.DiceString.roll_with_advantage") as mock_adv:
            mock_adv.return_value = (15, 15, 8)  # best=15, roll1=15, roll2=8

            with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
                mock_roll.return_value = (3, [3])  # damage roll

                result = resolve_attack(attacker, target, weapon, advantage=True)

                assert result.natural_roll == 15
                assert result.second_natural_roll == 8

    def test_disadvantage_populates_second_natural_roll(self, attacker, target, weapon):
        """Test that disadvantage populates second_natural_roll with discarded roll."""
        with patch("game.attack.DiceString.roll_with_disadvantage") as mock_dis:
            mock_dis.return_value = (8, 8, 15)  # worst=8, roll1=8, roll2=15

            result = resolve_attack(attacker, target, weapon, disadvantage=True)

            assert result.natural_roll == 8
            assert result.second_natural_roll == 15

    def test_normal_roll_has_no_second_natural_roll(self, attacker, target, weapon):
        """Test that a normal roll has no second_natural_roll."""
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.return_value = (5, [5])

            result = resolve_attack(attacker, target, weapon)

            assert result.second_natural_roll is None

    def test_advantage_and_disadvantage_cancel_out(self, attacker, target, weapon):
        """Test that both advantage and disadvantage cancel to single roll."""
        # Natural 15 + modifier 0 = 15, hits AC 15
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.side_effect = [(15, [15]), (2, [2])]

            result = resolve_attack(
                attacker,
                target,
                weapon,
                advantage=True,
                disadvantage=True,
            )

            assert result.second_natural_roll is None


class TestResolveAttackEdgeCases:
    """Additional edge case tests for attack resolution."""

    @pytest.fixture
    def weapon_no_damage(self):
        """Create a weapon with no damage field (should default to 1d4)."""
        settings, _ = WeaponSettings.objects.update_or_create(
            name=WeaponName.NET,
            defaults={
                "weapon_type": WeaponType.MARTIAL_RANGED,
                "cost": 1,
                "damage": None,
                "weight": 3,
                "properties": "special,thrown",
            },
        )
        return Weapon.objects.create(settings=settings)

    @pytest.fixture
    def attacker(self):
        """Create an attacker character."""
        character = CharacterFactory()
        character.level = 1

        str_ability = character.abilities.get(ability_type__name=AbilityName.STRENGTH)
        str_ability.score = 10
        str_ability.modifier = 0
        str_ability.save()

        dex_ability = character.abilities.get(ability_type__name=AbilityName.DEXTERITY)
        dex_ability.score = 10
        dex_ability.modifier = 0
        dex_ability.save()

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

    def test_attack_exactly_matches_ac(self, attacker, target, weapon_no_damage):
        """Test that an attack roll exactly equal to AC is a hit."""
        # Attacker has 0 modifier, natural 15 + 0 = 15, exactly equals AC
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.side_effect = [(15, [15]), (2, [2])]

            result = resolve_attack(attacker, target, weapon_no_damage)

            assert result.is_hit is True
            assert result.attack_roll == 15
            assert result.target_ac == 15

    def test_attack_one_below_ac_misses(self, attacker, target, weapon_no_damage):
        """Test that an attack roll one below AC is a miss."""
        # Natural 14 + 0 = 14, one below AC
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.return_value = (14, [14])

            result = resolve_attack(attacker, target, weapon_no_damage)

            assert result.is_hit is False
            assert result.damage == 0

    def test_weapon_with_no_damage_defaults_to_1d4(
        self, attacker, target, weapon_no_damage
    ):
        """Test that weapons with no damage field default to 1d4."""
        # Natural 20 + 0 = 20, hit (not crit since not nat 20 via the mock path)
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.side_effect = [(20, [20]), (3, [3]), (3, [3])]

            result = resolve_attack(attacker, target, weapon_no_damage)

            assert result.damage_dice == "1d4"

    def test_natural_20_and_natural_1_flags_mutually_exclusive(
        self, attacker, target, weapon_no_damage
    ):
        """Test that natural 20 and natural 1 cannot both be true."""
        # Natural 20 case
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.side_effect = [(20, [20]), (2, [2]), (2, [2])]

            result = resolve_attack(attacker, target, weapon_no_damage)

            assert result.is_critical_hit is True
            assert result.is_critical_miss is False

        # Natural 1 case
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.return_value = (1, [1])

            result = resolve_attack(attacker, target, weapon_no_damage)

            assert result.is_critical_hit is False
            assert result.is_critical_miss is True

    def test_both_advantage_and_disadvantage_cancel(
        self, attacker, target, weapon_no_damage
    ):
        """Test that both advantage and disadvantage cancel to single roll."""
        # When both advantage and disadvantage, uses roll_keeping_individual (single)
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.side_effect = [(15, [15]), (2, [2])]

            result = resolve_attack(
                attacker,
                target,
                weapon_no_damage,
                advantage=True,
                disadvantage=True,
            )

            assert result.is_hit is True
            assert result.second_natural_roll is None


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

    def test_apply_damage_absorbs_temp_hp(self, target):
        """Test that temp HP absorbs damage before real HP."""
        target.temp_hp = 5
        target.save()

        remaining = apply_damage(target, 8)

        target.refresh_from_db()
        assert target.temp_hp == 0
        assert target.hp == 17  # 20 - (8 - 5) = 17
        assert remaining == 17

    def test_apply_damage_temp_hp_fully_absorbs(self, target):
        """Test that temp HP can fully absorb damage."""
        target.temp_hp = 10
        target.save()

        remaining = apply_damage(target, 5)

        target.refresh_from_db()
        assert target.temp_hp == 5
        assert target.hp == 20  # No real HP lost
        assert remaining == 20

    def test_apply_damage_resets_death_saves_at_zero_hp(self, target):
        """Test that death save counters reset when HP drops to 0."""
        target.death_save_successes = 2
        target.death_save_failures = 1
        target.save()

        remaining = apply_damage(target, 100)

        target.refresh_from_db()
        assert remaining == 0
        assert target.death_save_successes == 0
        assert target.death_save_failures == 0
