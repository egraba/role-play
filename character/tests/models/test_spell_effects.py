import pytest

from magic.constants.spells import (
    EffectDurationType,
    SpellDamageType,
    SpellEffectType,
    SpellSaveEffect,
    SpellSaveType,
    SpellTargetType,
)
from magic.models.spell_effects import (
    ActiveSpellEffect,
    SpellEffectTemplate,
    SummonedCreature,
)

from ..factories import (
    ActiveSpellEffectFactory,
    CharacterFactory,
    ConditionFactory,
    SpellEffectTemplateFactory,
    SpellSettingsFactory,
    SummonedCreatureFactory,
)


@pytest.mark.django_db
class TestSpellEffectTemplateModel:
    def test_creation(self):
        spell = SpellSettingsFactory(name="Fireball")
        template = SpellEffectTemplate.objects.create(
            spell=spell,
            effect_type=SpellEffectType.DAMAGE,
            target_type=SpellTargetType.AREA,
            damage_type=SpellDamageType.FIRE,
            base_dice="8d6",
            dice_per_level="1d6",
            save_type=SpellSaveType.DEXTERITY,
            save_effect=SpellSaveEffect.HALF_DAMAGE,
            area_radius=20,
            area_shape="sphere",
            duration_type=EffectDurationType.INSTANTANEOUS,
        )
        assert template.spell == spell
        assert template.effect_type == SpellEffectType.DAMAGE
        assert template.target_type == SpellTargetType.AREA
        assert template.damage_type == SpellDamageType.FIRE
        assert template.base_dice == "8d6"
        assert template.dice_per_level == "1d6"
        assert template.save_type == SpellSaveType.DEXTERITY
        assert template.save_effect == SpellSaveEffect.HALF_DAMAGE
        assert template.area_radius == 20
        assert template.area_shape == "sphere"

    def test_str(self):
        spell = SpellSettingsFactory(name="Fireball")
        template = SpellEffectTemplateFactory(
            spell=spell,
            effect_type=SpellEffectType.DAMAGE,
        )
        assert "Fireball" in str(template)
        assert "Damage" in str(template)

    def test_healing_effect(self):
        spell = SpellSettingsFactory(name="Cure Wounds")
        template = SpellEffectTemplate.objects.create(
            spell=spell,
            effect_type=SpellEffectType.HEALING,
            target_type=SpellTargetType.SINGLE,
            base_dice="1d8",
            dice_per_level="1d8",
            duration_type=EffectDurationType.INSTANTANEOUS,
        )
        assert template.effect_type == SpellEffectType.HEALING
        assert template.base_dice == "1d8"

    def test_condition_effect(self):
        spell = SpellSettingsFactory(name="Hold Person")
        condition = ConditionFactory(name="paralyzed")
        template = SpellEffectTemplate.objects.create(
            spell=spell,
            effect_type=SpellEffectType.CONDITION,
            target_type=SpellTargetType.SINGLE,
            condition=condition,
            save_type=SpellSaveType.WISDOM,
            save_effect=SpellSaveEffect.NEGATES,
            duration_type=EffectDurationType.CONCENTRATION,
            duration_value=1,
        )
        assert template.condition == condition
        assert template.save_type == SpellSaveType.WISDOM
        assert template.save_effect == SpellSaveEffect.NEGATES

    def test_buff_effect(self):
        spell = SpellSettingsFactory(name="Shield of Faith")
        template = SpellEffectTemplate.objects.create(
            spell=spell,
            effect_type=SpellEffectType.BUFF,
            target_type=SpellTargetType.SINGLE,
            buff_description="+2 bonus to AC",
            ac_modifier=2,
            duration_type=EffectDurationType.CONCENTRATION,
            duration_value=10,
        )
        assert template.effect_type == SpellEffectType.BUFF
        assert template.ac_modifier == 2
        assert template.buff_description == "+2 bonus to AC"

    def test_debuff_effect(self):
        spell = SpellSettingsFactory(name="Bane")
        template = SpellEffectTemplate.objects.create(
            spell=spell,
            effect_type=SpellEffectType.DEBUFF,
            target_type=SpellTargetType.MULTIPLE,
            buff_description="-1d4 penalty to attacks and saves",
            attack_modifier=-2,
            save_type=SpellSaveType.CHARISMA,
            save_effect=SpellSaveEffect.NEGATES,
            duration_type=EffectDurationType.CONCENTRATION,
            duration_value=1,
        )
        assert template.effect_type == SpellEffectType.DEBUFF
        assert template.attack_modifier == -2

    def test_all_effect_types_valid(self):
        spell = SpellSettingsFactory()
        for effect_type, _ in SpellEffectType.choices:
            template = SpellEffectTemplateFactory(
                spell=spell,
                effect_type=effect_type,
            )
            assert template.effect_type == effect_type

    def test_all_target_types_valid(self):
        for target_type, _ in SpellTargetType.choices:
            template = SpellEffectTemplateFactory(target_type=target_type)
            assert template.target_type == target_type

    def test_all_save_types_valid(self):
        for save_type, _ in SpellSaveType.choices:
            template = SpellEffectTemplateFactory(save_type=save_type)
            assert template.save_type == save_type

    def test_all_damage_types_valid(self):
        for damage_type, _ in SpellDamageType.choices:
            template = SpellEffectTemplateFactory(damage_type=damage_type)
            assert template.damage_type == damage_type

    def test_all_duration_types_valid(self):
        for duration_type, _ in EffectDurationType.choices:
            template = SpellEffectTemplateFactory(duration_type=duration_type)
            assert template.duration_type == duration_type

    def test_spell_effect_templates_relation(self):
        spell = SpellSettingsFactory()
        template1 = SpellEffectTemplateFactory(spell=spell)
        SpellEffectTemplateFactory(spell=spell)

        assert spell.effect_templates.count() == 2
        assert template1 in spell.effect_templates.all()

    def test_cascade_delete_on_spell(self):
        template = SpellEffectTemplateFactory()
        spell_name = template.spell.name
        template.spell.delete()
        assert not SpellEffectTemplate.objects.filter(spell__name=spell_name).exists()


@pytest.mark.django_db
class TestActiveSpellEffectModel:
    def test_creation(self):
        character = CharacterFactory()
        caster = CharacterFactory()
        template = SpellEffectTemplateFactory()
        effect = ActiveSpellEffect.objects.create(
            character=character,
            template=template,
            caster=caster,
            rounds_remaining=10,
            is_concentration=True,
        )
        assert effect.character == character
        assert effect.template == template
        assert effect.caster == caster
        assert effect.rounds_remaining == 10
        assert effect.is_concentration is True

    def test_str(self):
        character = CharacterFactory(name="Gandalf")
        spell = SpellSettingsFactory(name="Haste")
        template = SpellEffectTemplateFactory(spell=spell)
        effect = ActiveSpellEffectFactory(character=character, template=template)
        assert "Gandalf" in str(effect)
        assert "Haste" in str(effect)

    def test_decrement_rounds_continues(self):
        effect = ActiveSpellEffectFactory(rounds_remaining=5)
        should_end = effect.decrement_rounds()
        assert should_end is False
        assert effect.rounds_remaining == 4

    def test_decrement_rounds_ends(self):
        effect = ActiveSpellEffectFactory(rounds_remaining=1)
        should_end = effect.decrement_rounds()
        assert should_end is True
        assert effect.rounds_remaining == 0

    def test_decrement_rounds_null_duration(self):
        effect = ActiveSpellEffectFactory(rounds_remaining=None)
        should_end = effect.decrement_rounds()
        assert should_end is False
        assert effect.rounds_remaining is None

    def test_end_effect(self):
        effect = ActiveSpellEffectFactory()
        effect_id = effect.id
        effect.end_effect()
        assert not ActiveSpellEffect.objects.filter(id=effect_id).exists()

    def test_character_active_spell_effects_relation(self):
        character = CharacterFactory()
        effect1 = ActiveSpellEffectFactory(character=character)
        ActiveSpellEffectFactory(character=character)

        assert character.active_spell_effects.count() == 2
        assert effect1 in character.active_spell_effects.all()

    def test_caster_cast_effects_relation(self):
        caster = CharacterFactory()
        effect1 = ActiveSpellEffectFactory(caster=caster)
        ActiveSpellEffectFactory(caster=caster)

        assert caster.cast_effects.count() == 2
        assert effect1 in caster.cast_effects.all()

    def test_cascade_delete_on_character(self):
        effect = ActiveSpellEffectFactory()
        character_id = effect.character.id
        effect.character.delete()
        assert not ActiveSpellEffect.objects.filter(character_id=character_id).exists()

    def test_cascade_delete_on_template(self):
        effect = ActiveSpellEffectFactory()
        template_id = effect.template.id
        effect.template.delete()
        assert not ActiveSpellEffect.objects.filter(template_id=template_id).exists()


@pytest.mark.django_db
class TestSummonedCreatureModel:
    def test_creation(self):
        summoner = CharacterFactory()
        spell = SpellSettingsFactory(name="Conjure Animals")
        creature = SummonedCreature.objects.create(
            summoner=summoner,
            spell=spell,
            name="Wolf",
            hp_current=11,
            hp_max=11,
            ac=13,
            rounds_remaining=60,
            is_concentration=True,
        )
        assert creature.summoner == summoner
        assert creature.spell == spell
        assert creature.name == "Wolf"
        assert creature.hp_current == 11
        assert creature.hp_max == 11
        assert creature.ac == 13
        assert creature.rounds_remaining == 60
        assert creature.is_concentration is True

    def test_str(self):
        summoner = CharacterFactory(name="Druid")
        creature = SummonedCreatureFactory(summoner=summoner, name="Bear")
        assert "Bear" in str(creature)
        assert "Druid" in str(creature)

    def test_take_damage(self):
        creature = SummonedCreatureFactory(hp_current=20, hp_max=20)
        remaining = creature.take_damage(5)
        assert remaining == 15
        assert creature.hp_current == 15

    def test_take_damage_not_below_zero(self):
        creature = SummonedCreatureFactory(hp_current=10, hp_max=20)
        remaining = creature.take_damage(15)
        assert remaining == 0
        assert creature.hp_current == 0

    def test_heal(self):
        creature = SummonedCreatureFactory(hp_current=10, hp_max=20)
        new_hp = creature.heal(5)
        assert new_hp == 15
        assert creature.hp_current == 15

    def test_heal_not_above_max(self):
        creature = SummonedCreatureFactory(hp_current=15, hp_max=20)
        new_hp = creature.heal(10)
        assert new_hp == 20
        assert creature.hp_current == 20

    def test_is_alive_true(self):
        creature = SummonedCreatureFactory(hp_current=1)
        assert creature.is_alive() is True

    def test_is_alive_false(self):
        creature = SummonedCreatureFactory(hp_current=0)
        assert creature.is_alive() is False

    def test_dismiss(self):
        creature = SummonedCreatureFactory()
        creature_id = creature.id
        creature.dismiss()
        assert not SummonedCreature.objects.filter(id=creature_id).exists()

    def test_summoner_summoned_creatures_relation(self):
        summoner = CharacterFactory()
        creature1 = SummonedCreatureFactory(summoner=summoner)
        SummonedCreatureFactory(summoner=summoner)

        assert summoner.summoned_creatures.count() == 2
        assert creature1 in summoner.summoned_creatures.all()

    def test_cascade_delete_on_summoner(self):
        creature = SummonedCreatureFactory()
        summoner_id = creature.summoner.id
        creature.summoner.delete()
        assert not SummonedCreature.objects.filter(summoner_id=summoner_id).exists()

    def test_combat_relation_optional(self):
        creature = SummonedCreatureFactory(combat=None)
        assert creature.combat is None

    def test_cascade_delete_on_spell(self):
        creature = SummonedCreatureFactory()
        spell_pk = creature.spell.pk
        creature.spell.delete()
        assert not SummonedCreature.objects.filter(spell=spell_pk).exists()


@pytest.mark.django_db
class TestSpellEffectTemplateDefaults:
    """Tests for default values on SpellEffectTemplate."""

    def test_default_save_type(self):
        spell = SpellSettingsFactory()
        template = SpellEffectTemplate.objects.create(
            spell=spell,
            effect_type=SpellEffectType.DAMAGE,
            target_type=SpellTargetType.SINGLE,
            duration_type=EffectDurationType.INSTANTANEOUS,
        )
        assert template.save_type == SpellSaveType.NONE

    def test_default_save_effect(self):
        spell = SpellSettingsFactory()
        template = SpellEffectTemplate.objects.create(
            spell=spell,
            effect_type=SpellEffectType.DAMAGE,
            target_type=SpellTargetType.SINGLE,
            duration_type=EffectDurationType.INSTANTANEOUS,
        )
        assert template.save_effect == SpellSaveEffect.NONE

    def test_default_modifiers_are_zero(self):
        spell = SpellSettingsFactory()
        template = SpellEffectTemplate.objects.create(
            spell=spell,
            effect_type=SpellEffectType.BUFF,
            target_type=SpellTargetType.SINGLE,
            duration_type=EffectDurationType.ROUNDS,
            duration_value=10,
        )
        assert template.ac_modifier == 0
        assert template.attack_modifier == 0
        assert template.damage_modifier == 0

    def test_default_area_radius_is_zero(self):
        spell = SpellSettingsFactory()
        template = SpellEffectTemplate.objects.create(
            spell=spell,
            effect_type=SpellEffectType.DAMAGE,
            target_type=SpellTargetType.SINGLE,
            duration_type=EffectDurationType.INSTANTANEOUS,
        )
        assert template.area_radius == 0

    def test_default_duration_value_is_zero(self):
        spell = SpellSettingsFactory()
        template = SpellEffectTemplate.objects.create(
            spell=spell,
            effect_type=SpellEffectType.DAMAGE,
            target_type=SpellTargetType.SINGLE,
            duration_type=EffectDurationType.INSTANTANEOUS,
        )
        assert template.duration_value == 0

    def test_blank_fields_allowed(self):
        spell = SpellSettingsFactory()
        template = SpellEffectTemplate.objects.create(
            spell=spell,
            effect_type=SpellEffectType.UTILITY,
            target_type=SpellTargetType.SELF,
            duration_type=EffectDurationType.INSTANTANEOUS,
            # All optional fields left blank
        )
        assert template.damage_type == ""
        assert template.base_dice == ""
        assert template.dice_per_level == ""
        assert template.buff_description == ""
        assert template.area_shape == ""
        assert template.condition is None


@pytest.mark.django_db
class TestActiveSpellEffectConcentration:
    """Tests for concentration-related functionality."""

    def test_concentration_effect_creation(self):
        effect = ActiveSpellEffectFactory(is_concentration=True)
        assert effect.is_concentration is True

    def test_non_concentration_effect_creation(self):
        effect = ActiveSpellEffectFactory(is_concentration=False)
        assert effect.is_concentration is False

    def test_multiple_concentration_effects_same_caster(self):
        caster = CharacterFactory()
        effect1 = ActiveSpellEffectFactory(caster=caster, is_concentration=True)
        effect2 = ActiveSpellEffectFactory(caster=caster, is_concentration=True)

        # Both effects can exist (game logic should handle concentration limits)
        assert effect1.caster == caster
        assert effect2.caster == caster
        assert caster.cast_effects.count() == 2


@pytest.mark.django_db
class TestSummonedCreatureEdgeCases:
    """Edge case tests for SummonedCreature model."""

    def test_take_damage_exact_hp(self):
        creature = SummonedCreatureFactory(hp_current=10, hp_max=20)
        remaining = creature.take_damage(10)
        assert remaining == 0
        assert creature.hp_current == 0
        assert creature.is_alive() is False

    def test_heal_from_zero(self):
        creature = SummonedCreatureFactory(hp_current=0, hp_max=20)
        new_hp = creature.heal(5)
        assert new_hp == 5
        assert creature.hp_current == 5
        assert creature.is_alive() is True

    def test_heal_exact_to_max(self):
        creature = SummonedCreatureFactory(hp_current=15, hp_max=20)
        new_hp = creature.heal(5)
        assert new_hp == 20
        assert creature.hp_current == 20

    def test_take_zero_damage(self):
        creature = SummonedCreatureFactory(hp_current=15, hp_max=20)
        remaining = creature.take_damage(0)
        assert remaining == 15
        assert creature.hp_current == 15

    def test_heal_zero(self):
        creature = SummonedCreatureFactory(hp_current=10, hp_max=20)
        new_hp = creature.heal(0)
        assert new_hp == 10
        assert creature.hp_current == 10
