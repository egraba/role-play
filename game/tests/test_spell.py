"""Tests for the spell resolution system."""

from unittest.mock import patch

import pytest

from character.constants.abilities import AbilityName
from character.constants.classes import ClassName
from character.constants.conditions import ConditionName
from character.constants.spells import (
    CasterType,
    EffectDurationType,
    SpellDamageType,
    SpellEffectType,
    SpellLevel,
    SpellSaveEffect,
    SpellSaveType,
    SpellcastingAbility,
)
from character.models import (
    CharacterCondition,
    Concentration,
)
from character.tests.factories import (
    CharacterClassFactory,
    CharacterFactory,
    ClassFactory,
    ClassSpellcastingFactory,
    ConditionFactory,
    SpellEffectTemplateFactory,
    SpellSettingsFactory,
)

from game.spell import (
    SpellBuffResult,
    SpellCastResult,
    SpellConditionResult,
    SpellDamageResult,
    SpellHealingResult,
    SpellSaveResult,
    apply_spell_buff,
    apply_spell_condition,
    apply_spell_damage,
    apply_spell_healing,
    apply_spell_result,
    calculate_spell_dice,
    get_saving_throw_modifier,
    get_spell_save_dc,
    get_spellcasting_ability_modifier,
    resolve_saving_throw,
    resolve_spell,
    resolve_spell_buff,
    resolve_spell_condition,
    resolve_spell_damage,
    resolve_spell_healing,
)

pytestmark = pytest.mark.django_db


class TestGetSpellcastingAbilityModifier:
    """Tests for getting the spellcasting ability modifier."""

    @pytest.fixture
    def wizard(self):
        """Create a wizard character with INT as spellcasting ability."""
        character = CharacterFactory()

        klass = ClassFactory(name=ClassName.WIZARD)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PREPARED,
            spellcasting_ability=SpellcastingAbility.INTELLIGENCE,
        )
        CharacterClassFactory(character=character, klass=klass, is_primary=True)

        int_ability = character.abilities.get(
            ability_type__name=AbilityName.INTELLIGENCE
        )
        int_ability.score = 18
        int_ability.modifier = 4
        int_ability.save()

        return character

    @pytest.fixture
    def cleric(self):
        """Create a cleric character with WIS as spellcasting ability."""
        character = CharacterFactory()

        klass = ClassFactory(name=ClassName.CLERIC)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PREPARED,
            spellcasting_ability=SpellcastingAbility.WISDOM,
        )
        CharacterClassFactory(character=character, klass=klass, is_primary=True)

        wis_ability = character.abilities.get(ability_type__name=AbilityName.WISDOM)
        wis_ability.score = 16
        wis_ability.modifier = 3
        wis_ability.save()

        return character

    @pytest.fixture
    def non_caster(self):
        """Create a non-caster character."""
        character = CharacterFactory()

        klass = ClassFactory(name=ClassName.FIGHTER)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type="",  # Non-caster
            spellcasting_ability="",
        )
        CharacterClassFactory(character=character, klass=klass, is_primary=True)

        return character

    def test_wizard_uses_intelligence(self, wizard):
        """Test that wizards use Intelligence for spellcasting."""
        modifier = get_spellcasting_ability_modifier(wizard)
        assert modifier == 4

    def test_cleric_uses_wisdom(self, cleric):
        """Test that clerics use Wisdom for spellcasting."""
        modifier = get_spellcasting_ability_modifier(cleric)
        assert modifier == 3

    def test_non_caster_returns_zero(self, non_caster):
        """Test that non-casters return 0."""
        modifier = get_spellcasting_ability_modifier(non_caster)
        assert modifier == 0

    def test_character_without_class_returns_zero(self):
        """Test that characters without a class return 0."""
        character = CharacterFactory()
        modifier = get_spellcasting_ability_modifier(character)
        assert modifier == 0


class TestGetSpellSaveDC:
    """Tests for spell save DC calculation."""

    @pytest.fixture
    def wizard(self):
        """Create a level 5 wizard with INT 18."""
        character = CharacterFactory()
        character.level = 5  # Proficiency +3
        character.save()

        klass = ClassFactory(name=ClassName.WIZARD)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PREPARED,
            spellcasting_ability=SpellcastingAbility.INTELLIGENCE,
        )
        CharacterClassFactory(character=character, klass=klass, is_primary=True)

        int_ability = character.abilities.get(
            ability_type__name=AbilityName.INTELLIGENCE
        )
        int_ability.score = 18
        int_ability.modifier = 4
        int_ability.save()

        return character

    def test_spell_save_dc_calculation(self, wizard):
        """Test DC = 8 + proficiency + ability modifier."""
        # Level 5 = +3 proficiency, INT 18 = +4 modifier
        # DC = 8 + 3 + 4 = 15
        dc = get_spell_save_dc(wizard)
        assert dc == 15


class TestGetSavingThrowModifier:
    """Tests for saving throw modifier calculation."""

    @pytest.fixture
    def character(self):
        """Create a character with known ability modifiers."""
        character = CharacterFactory()
        character.level = 5
        character.save()

        dex_ability = character.abilities.get(ability_type__name=AbilityName.DEXTERITY)
        dex_ability.score = 16
        dex_ability.modifier = 3
        dex_ability.save()

        return character

    def test_saving_throw_modifier_without_proficiency(self, character):
        """Test saving throw modifier is just ability modifier without proficiency."""
        modifier = get_saving_throw_modifier(character, SpellSaveType.DEXTERITY)
        assert modifier == 3

    def test_invalid_save_type_returns_zero(self, character):
        """Test invalid save type returns 0."""
        modifier = get_saving_throw_modifier(character, "invalid")
        assert modifier == 0


class TestResolveSavingThrow:
    """Tests for saving throw resolution."""

    @pytest.fixture
    def character(self):
        """Create a character for saving throw tests."""
        character = CharacterFactory()

        dex_ability = character.abilities.get(ability_type__name=AbilityName.DEXTERITY)
        dex_ability.score = 14
        dex_ability.modifier = 2
        dex_ability.save()

        return character

    def test_successful_save(self, character):
        """Test a successful saving throw."""
        with patch("game.spell.roll_d20_test") as mock_roll:
            mock_roll.return_value = (17, False, False)  # Total 17

            result = resolve_saving_throw(character, SpellSaveType.DEXTERITY, dc=15)

            assert result.success is True
            assert result.dc == 15
            assert result.roll == 17
            assert result.save_type == SpellSaveType.DEXTERITY

    def test_failed_save(self, character):
        """Test a failed saving throw."""
        with patch("game.spell.roll_d20_test") as mock_roll:
            mock_roll.return_value = (12, False, False)  # Total 12

            result = resolve_saving_throw(character, SpellSaveType.DEXTERITY, dc=15)

            assert result.success is False
            assert result.dc == 15
            assert result.roll == 12

    def test_exact_dc_succeeds(self, character):
        """Test that meeting the DC exactly is a success."""
        with patch("game.spell.roll_d20_test") as mock_roll:
            mock_roll.return_value = (15, False, False)  # Exactly DC

            result = resolve_saving_throw(character, SpellSaveType.DEXTERITY, dc=15)

            assert result.success is True


class TestCalculateSpellDice:
    """Tests for spell dice calculation with upcasting."""

    def test_base_dice_no_upcast(self):
        """Test base dice without upcasting."""
        spell = SpellSettingsFactory(level=SpellLevel.THIRD)
        template = SpellEffectTemplateFactory(
            spell=spell,
            base_dice="8d6",
            dice_per_level="1d6",
        )

        dice_str = calculate_spell_dice(template, slot_level=3)
        assert dice_str == "8d6"

    def test_upcast_adds_dice(self):
        """Test that upcasting adds extra dice."""
        spell = SpellSettingsFactory(level=SpellLevel.THIRD)
        template = SpellEffectTemplateFactory(
            spell=spell,
            base_dice="8d6",
            dice_per_level="1d6",
        )

        dice_str = calculate_spell_dice(template, slot_level=5)
        # 2 levels above base = 2 extra dice
        assert dice_str == "10d6"

    def test_empty_base_dice_returns_empty(self):
        """Test empty base_dice returns empty string."""
        spell = SpellSettingsFactory()
        template = SpellEffectTemplateFactory(
            spell=spell,
            base_dice="",
            dice_per_level="",
        )

        dice_str = calculate_spell_dice(template, slot_level=3)
        assert dice_str == ""


class TestResolveSpellDamage:
    """Tests for spell damage resolution."""

    def test_damage_resolution(self):
        """Test basic damage resolution."""
        spell = SpellSettingsFactory(level=SpellLevel.THIRD)
        template = SpellEffectTemplateFactory(
            spell=spell,
            effect_type=SpellEffectType.DAMAGE,
            damage_type=SpellDamageType.FIRE,
            base_dice="8d6",
        )

        with patch("game.spell.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.return_value = (28, [4, 3, 5, 2, 6, 3, 4, 1])

            result = resolve_spell_damage(template, slot_level=3)

            assert result.total == 28
            assert result.damage_type == SpellDamageType.FIRE
            assert result.halved is False
            assert len(result.dice_rolled) == 8

    def test_damage_halved_on_successful_save(self):
        """Test that damage is halved on successful save."""
        spell = SpellSettingsFactory(level=SpellLevel.THIRD)
        template = SpellEffectTemplateFactory(
            spell=spell,
            effect_type=SpellEffectType.DAMAGE,
            save_type=SpellSaveType.DEXTERITY,
            save_effect=SpellSaveEffect.HALF_DAMAGE,
            base_dice="8d6",
        )
        save_result = SpellSaveResult(
            save_type=SpellSaveType.DEXTERITY,
            dc=15,
            roll=18,
            modifier=3,
            success=True,
        )

        with patch("game.spell.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.return_value = (28, [4, 3, 5, 2, 6, 3, 4, 1])

            result = resolve_spell_damage(
                template, slot_level=3, save_result=save_result
            )

            assert result.total == 14  # 28 // 2
            assert result.halved is True

    def test_damage_not_halved_on_failed_save(self):
        """Test that damage is not halved on failed save."""
        spell = SpellSettingsFactory(level=SpellLevel.THIRD)
        template = SpellEffectTemplateFactory(
            spell=spell,
            effect_type=SpellEffectType.DAMAGE,
            save_effect=SpellSaveEffect.HALF_DAMAGE,
            base_dice="8d6",
        )
        save_result = SpellSaveResult(
            save_type=SpellSaveType.DEXTERITY,
            dc=15,
            roll=10,
            modifier=3,
            success=False,
        )

        with patch("game.spell.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.return_value = (28, [4, 3, 5, 2, 6, 3, 4, 1])

            result = resolve_spell_damage(
                template, slot_level=3, save_result=save_result
            )

            assert result.total == 28
            assert result.halved is False


class TestResolveSpellHealing:
    """Tests for spell healing resolution."""

    @pytest.fixture
    def cleric(self):
        """Create a cleric with WIS 16 (+3)."""
        character = CharacterFactory()

        klass = ClassFactory(name=ClassName.CLERIC)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PREPARED,
            spellcasting_ability=SpellcastingAbility.WISDOM,
        )
        CharacterClassFactory(character=character, klass=klass, is_primary=True)

        wis_ability = character.abilities.get(ability_type__name=AbilityName.WISDOM)
        wis_ability.score = 16
        wis_ability.modifier = 3
        wis_ability.save()

        return character

    def test_healing_resolution(self, cleric):
        """Test basic healing resolution."""
        spell = SpellSettingsFactory(level=SpellLevel.FIRST)
        template = SpellEffectTemplateFactory(
            spell=spell,
            effect_type=SpellEffectType.HEALING,
            base_dice="1d8",
        )

        with patch("game.spell.DiceString.roll_keeping_individual") as mock_roll:
            mock_roll.return_value = (5, [5])

            result = resolve_spell_healing(template, slot_level=1, caster=cleric)

            # 5 (dice) + 3 (WIS mod) = 8
            assert result.total == 8
            assert result.dice_rolled == [5]


class TestResolveSpellCondition:
    """Tests for spell condition resolution."""

    def test_condition_applied(self):
        """Test condition is applied when save fails."""
        condition = ConditionFactory(name=ConditionName.PARALYZED)
        spell = SpellSettingsFactory()
        template = SpellEffectTemplateFactory(
            spell=spell,
            effect_type=SpellEffectType.CONDITION,
            condition=condition,
            save_effect=SpellSaveEffect.NEGATES,
            duration_type=EffectDurationType.ROUNDS,
            duration_value=10,
        )
        save_result = SpellSaveResult(
            save_type=SpellSaveType.WISDOM,
            dc=15,
            roll=12,
            modifier=2,
            success=False,
        )

        result = resolve_spell_condition(template, save_result=save_result)

        assert result.applied is True
        assert result.condition == condition
        assert result.duration_rounds == 10

    def test_condition_negated_on_save(self):
        """Test condition is negated on successful save."""
        condition = ConditionFactory(name=ConditionName.PARALYZED)
        spell = SpellSettingsFactory()
        template = SpellEffectTemplateFactory(
            spell=spell,
            effect_type=SpellEffectType.CONDITION,
            condition=condition,
            save_effect=SpellSaveEffect.NEGATES,
        )
        save_result = SpellSaveResult(
            save_type=SpellSaveType.WISDOM,
            dc=15,
            roll=18,
            modifier=3,
            success=True,
        )

        result = resolve_spell_condition(template, save_result=save_result)

        assert result.applied is False

    def test_no_condition_returns_none(self):
        """Test that no condition template returns None."""
        spell = SpellSettingsFactory()
        template = SpellEffectTemplateFactory(
            spell=spell,
            effect_type=SpellEffectType.DAMAGE,
            condition=None,
        )

        result = resolve_spell_condition(template)

        assert result is None


class TestResolveSpellBuff:
    """Tests for spell buff resolution."""

    def test_buff_resolution(self):
        """Test buff effect resolution."""
        spell = SpellSettingsFactory()
        template = SpellEffectTemplateFactory(
            spell=spell,
            effect_type=SpellEffectType.BUFF,
            buff_description="+2 bonus to AC",
            ac_modifier=2,
            duration_type=EffectDurationType.ROUNDS,
            duration_value=10,
        )

        result = resolve_spell_buff(template)

        assert result.description == "+2 bonus to AC"
        assert result.ac_modifier == 2
        assert result.duration_rounds == 10


class TestResolveSpell:
    """Tests for the main spell resolution function."""

    @pytest.fixture
    def caster(self):
        """Create a caster character."""
        character = CharacterFactory()
        character.level = 5
        character.save()

        klass = ClassFactory(name=ClassName.WIZARD)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PREPARED,
            spellcasting_ability=SpellcastingAbility.INTELLIGENCE,
        )
        CharacterClassFactory(character=character, klass=klass, is_primary=True)

        int_ability = character.abilities.get(
            ability_type__name=AbilityName.INTELLIGENCE
        )
        int_ability.score = 16
        int_ability.modifier = 3
        int_ability.save()

        return character

    @pytest.fixture
    def target(self):
        """Create a target character."""
        character = CharacterFactory()
        character.hp = 30
        character.max_hp = 30
        character.save()
        return character

    def test_resolve_damage_spell(self, caster, target):
        """Test resolving a damage spell."""
        spell = SpellSettingsFactory(level=SpellLevel.THIRD)
        SpellEffectTemplateFactory(
            spell=spell,
            effect_type=SpellEffectType.DAMAGE,
            damage_type=SpellDamageType.FIRE,
            base_dice="8d6",
            save_type=SpellSaveType.DEXTERITY,
            save_effect=SpellSaveEffect.HALF_DAMAGE,
        )

        with patch("game.spell.roll_d20_test") as mock_save:
            mock_save.return_value = (12, False, False)  # Failed save

            with patch("game.spell.DiceString.roll_keeping_individual") as mock_damage:
                mock_damage.return_value = (28, [4, 3, 5, 2, 6, 3, 4, 1])

                result = resolve_spell(caster, spell, [target], slot_level=3)

                assert result.success is True
                assert len(result.damage_results) == 1
                assert result.damage_results[0][0] == target
                assert result.damage_results[0][1].total == 28

    def test_resolve_healing_spell(self, caster, target):
        """Test resolving a healing spell."""
        spell = SpellSettingsFactory(level=SpellLevel.FIRST)
        SpellEffectTemplateFactory(
            spell=spell,
            effect_type=SpellEffectType.HEALING,
            base_dice="1d8",
        )

        with patch("game.spell.DiceString.roll_keeping_individual") as mock_heal:
            mock_heal.return_value = (5, [5])

            result = resolve_spell(caster, spell, [target], slot_level=1)

            assert len(result.healing_results) == 1
            assert result.healing_results[0][0] == target

    def test_concentration_spell_marks_concentration(self, caster, target):
        """Test that concentration spells mark concentration_started."""
        spell = SpellSettingsFactory(level=SpellLevel.FIRST, concentration=True)
        SpellEffectTemplateFactory(
            spell=spell,
            effect_type=SpellEffectType.BUFF,
            duration_type=EffectDurationType.CONCENTRATION,
        )

        result = resolve_spell(caster, spell, [target], slot_level=1)

        assert result.concentration_started is True


class TestApplySpellDamage:
    """Tests for applying spell damage."""

    @pytest.fixture
    def target(self):
        """Create a target character."""
        character = CharacterFactory()
        character.hp = 30
        character.max_hp = 30
        character.save()
        return character

    def test_apply_damage_reduces_hp(self, target):
        """Test that damage reduces HP."""
        result = SpellDamageResult(
            total=15,
            dice_rolled=[3, 4, 5, 3],
            damage_type=SpellDamageType.FIRE,
        )

        remaining = apply_spell_damage(target, result)

        target.refresh_from_db()
        assert remaining == 15
        assert target.hp == 15

    def test_apply_damage_not_below_zero(self, target):
        """Test that HP cannot go below 0."""
        result = SpellDamageResult(
            total=50,
            dice_rolled=[6, 6, 6, 6, 6, 6, 6, 6],
            damage_type=SpellDamageType.FIRE,
        )

        remaining = apply_spell_damage(target, result)

        target.refresh_from_db()
        assert remaining == 0
        assert target.hp == 0


class TestApplySpellHealing:
    """Tests for applying spell healing."""

    @pytest.fixture
    def target(self):
        """Create an injured target character."""
        character = CharacterFactory()
        character.hp = 10
        character.max_hp = 30
        character.save()
        return character

    def test_apply_healing_increases_hp(self, target):
        """Test that healing increases HP."""
        result = SpellHealingResult(total=8, dice_rolled=[5])

        new_hp = apply_spell_healing(target, result)

        target.refresh_from_db()
        assert new_hp == 18
        assert target.hp == 18

    def test_apply_healing_not_above_max(self, target):
        """Test that HP cannot exceed max."""
        result = SpellHealingResult(total=50, dice_rolled=[8])

        new_hp = apply_spell_healing(target, result)

        target.refresh_from_db()
        assert new_hp == 30
        assert target.hp == 30
        assert result.overheal == 30  # 10 + 50 = 60, but max is 30, so 30 overheal


class TestApplySpellCondition:
    """Tests for applying spell conditions."""

    @pytest.fixture
    def target(self):
        """Create a target character."""
        return CharacterFactory()

    def test_apply_condition_creates_character_condition(self, target):
        """Test that applying a condition creates CharacterCondition."""
        condition = ConditionFactory(name=ConditionName.PARALYZED)
        result = SpellConditionResult(
            condition=condition,
            applied=True,
            duration_rounds=10,
        )

        char_condition = apply_spell_condition(target, result)

        assert char_condition is not None
        assert char_condition.character == target
        assert char_condition.condition == condition

    def test_apply_condition_not_applied_returns_none(self, target):
        """Test that not applied condition returns None."""
        condition = ConditionFactory(name=ConditionName.PARALYZED)
        result = SpellConditionResult(
            condition=condition,
            applied=False,
            duration_rounds=None,
        )

        char_condition = apply_spell_condition(target, result)

        assert char_condition is None
        assert not CharacterCondition.objects.filter(
            character=target, condition=condition
        ).exists()


class TestApplySpellBuff:
    """Tests for applying spell buffs."""

    @pytest.fixture
    def target(self):
        """Create a target character."""
        return CharacterFactory()

    @pytest.fixture
    def caster(self):
        """Create a caster character."""
        return CharacterFactory()

    def test_apply_buff_creates_active_effect(self, target, caster):
        """Test that applying a buff creates ActiveSpellEffect."""
        spell = SpellSettingsFactory()
        template = SpellEffectTemplateFactory(
            spell=spell,
            effect_type=SpellEffectType.BUFF,
            duration_type=EffectDurationType.ROUNDS,
            duration_value=10,
        )
        result = SpellBuffResult(
            description="+2 AC",
            ac_modifier=2,
            attack_modifier=0,
            damage_modifier=0,
            duration_rounds=10,
        )

        active_effect = apply_spell_buff(target, result, template, caster)

        assert active_effect.character == target
        assert active_effect.caster == caster
        assert active_effect.template == template
        assert active_effect.rounds_remaining == 10


class TestApplySpellResult:
    """Tests for applying complete spell cast results."""

    @pytest.fixture
    def caster(self):
        """Create a caster character."""
        character = CharacterFactory()

        klass = ClassFactory(name=ClassName.WIZARD)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PREPARED,
            spellcasting_ability=SpellcastingAbility.INTELLIGENCE,
        )
        CharacterClassFactory(character=character, klass=klass, is_primary=True)

        return character

    @pytest.fixture
    def target(self):
        """Create a target character."""
        character = CharacterFactory()
        character.hp = 30
        character.max_hp = 30
        character.save()
        return character

    def test_apply_spell_result_applies_all_effects(self, caster, target):
        """Test that apply_spell_result applies all effects."""
        spell = SpellSettingsFactory(concentration=True)
        damage_result = SpellDamageResult(
            total=15,
            dice_rolled=[3, 4, 5, 3],
            damage_type=SpellDamageType.FIRE,
        )

        result = SpellCastResult(
            spell=spell,
            caster=caster,
            targets=[target],
            slot_level=3,
            success=True,
            damage_results=[(target, damage_result)],
            concentration_started=True,
        )

        apply_spell_result(result)

        target.refresh_from_db()
        assert target.hp == 15  # 30 - 15

        # Check concentration started
        assert Concentration.objects.filter(character=caster, spell=spell).exists()
