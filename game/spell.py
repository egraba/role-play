"""Spell resolution system for D&D 5e magic.

This module implements spell casting mechanics:
- Spell save DC calculation: 8 + proficiency bonus + spellcasting ability modifier
- Saving throws against spell effects
- Damage and healing resolution with scaling for higher-level slots
- Condition application
- Buff/debuff effect creation
- Apply functions to modify game state

Following the resolve/apply pattern from game.attack module.
"""

from dataclasses import dataclass, field

from character.constants.spells import (
    EffectDurationType,
    SpellEffectType,
    SpellSaveEffect,
    SpellSaveType,
)
from character.models import (
    ActiveSpellEffect,
    Character,
    CharacterCondition,
    Condition,
    SpellEffectTemplate,
    SpellSettings,
)
from utils.dice import DiceString, roll_d20_test


@dataclass
class SpellSaveResult:
    """Result of a saving throw against a spell effect."""

    save_type: str
    dc: int
    roll: int
    modifier: int
    success: bool


@dataclass
class SpellDamageResult:
    """Result of spell damage resolution."""

    total: int
    dice_rolled: list[int]
    damage_type: str
    is_critical: bool = False
    halved: bool = False


@dataclass
class SpellHealingResult:
    """Result of spell healing resolution."""

    total: int
    dice_rolled: list[int]
    overheal: int = 0


@dataclass
class SpellConditionResult:
    """Result of spell condition application."""

    condition: Condition
    applied: bool
    duration_rounds: int | None


@dataclass
class SpellBuffResult:
    """Result of spell buff/debuff application."""

    description: str
    ac_modifier: int
    attack_modifier: int
    damage_modifier: int
    duration_rounds: int | None


@dataclass
class SpellCastResult:
    """Complete result of casting a spell."""

    spell: SpellSettings
    caster: Character
    targets: list[Character]
    slot_level: int
    success: bool
    damage_results: list[tuple[Character, SpellDamageResult]] = field(
        default_factory=list
    )
    healing_results: list[tuple[Character, SpellHealingResult]] = field(
        default_factory=list
    )
    condition_results: list[tuple[Character, SpellConditionResult]] = field(
        default_factory=list
    )
    buff_results: list[tuple[Character, SpellBuffResult]] = field(default_factory=list)
    save_results: list[tuple[Character, SpellSaveResult]] = field(default_factory=list)
    concentration_started: bool = False


# Mapping from SpellcastingAbility to AbilityName
SPELLCASTING_ABILITY_MAP: dict[str, str] = {
    "intelligence": "INT",
    "wisdom": "WIS",
    "charisma": "CHA",
}

# Mapping from SpellSaveType to AbilityName
SAVE_TYPE_TO_ABILITY_MAP: dict[str, str] = {
    "STR": "STR",
    "DEX": "DEX",
    "CON": "CON",
    "INT": "INT",
    "WIS": "WIS",
    "CHA": "CHA",
}


def get_spellcasting_ability_modifier(caster: Character) -> int:
    """Get the caster's spellcasting ability modifier.

    Args:
        caster: The character casting the spell.

    Returns:
        The modifier for the character's spellcasting ability.
        Defaults to 0 if no spellcasting class is found.
    """
    # Get the primary class's spellcasting configuration
    primary_class = caster.primary_class
    if not primary_class:
        return 0

    try:
        spellcasting = primary_class.spellcasting
        if not spellcasting.is_caster:
            return 0

        # Map spellcasting ability to character ability
        ability_name = SPELLCASTING_ABILITY_MAP.get(spellcasting.spellcasting_ability)
        if not ability_name:
            return 0

        ability = caster.abilities.get(ability_type__name=ability_name)
        return ability.modifier
    except Exception:
        return 0


def get_spell_save_dc(caster: Character) -> int:
    """Calculate spell save DC: 8 + proficiency + spellcasting ability modifier.

    Args:
        caster: The character casting the spell.

    Returns:
        The spell save DC for this caster.
    """
    return 8 + caster.proficiency_bonus + get_spellcasting_ability_modifier(caster)


def get_saving_throw_modifier(target: Character, save_type: str) -> int:
    """Get the target's modifier for a specific saving throw.

    Args:
        target: The character making the save.
        save_type: The type of save (STR, DEX, CON, INT, WIS, CHA).

    Returns:
        The saving throw modifier including proficiency if applicable.
    """
    ability_name = SAVE_TYPE_TO_ABILITY_MAP.get(save_type)
    if not ability_name:
        return 0

    ability = target.abilities.get(ability_type__name=ability_name)
    modifier = ability.modifier

    # Add proficiency bonus if proficient in this save
    if target.is_proficient(ability):
        modifier += target.proficiency_bonus

    return modifier


def resolve_saving_throw(
    target: Character,
    save_type: str,
    dc: int,
    advantage: bool = False,
    disadvantage: bool = False,
) -> SpellSaveResult:
    """Roll a saving throw for the target against a spell effect.

    Args:
        target: The character making the save.
        save_type: The type of save required.
        dc: The difficulty class to meet or beat.
        advantage: Whether the target has advantage on the save.
        disadvantage: Whether the target has disadvantage on the save.

    Returns:
        SpellSaveResult with the roll details and success status.
    """
    modifier = get_saving_throw_modifier(target, save_type)
    roll, _, _ = roll_d20_test(
        modifier=modifier,
        advantage=advantage,
        disadvantage=disadvantage,
    )

    return SpellSaveResult(
        save_type=save_type,
        dc=dc,
        roll=roll,
        modifier=modifier,
        success=roll >= dc,
    )


def calculate_spell_dice(
    template: SpellEffectTemplate,
    slot_level: int,
) -> str:
    """Calculate the dice string for a spell effect at a given slot level.

    Args:
        template: The spell effect template.
        slot_level: The level of the spell slot used.

    Returns:
        A dice string like "8d6" for the total damage/healing dice.
    """
    if not template.base_dice:
        return ""

    base_dice = DiceString(template.base_dice)

    # Add extra dice for upcasting
    if template.dice_per_level and slot_level > template.spell.level:
        extra_levels = slot_level - template.spell.level
        per_level = DiceString(template.dice_per_level)
        extra_dice_count = per_level.nb_throws * extra_levels
        if extra_dice_count > 0:
            base_dice.add_throws(extra_dice_count)

    return str(base_dice)


def resolve_spell_damage(
    template: SpellEffectTemplate,
    slot_level: int,
    save_result: SpellSaveResult | None = None,
) -> SpellDamageResult:
    """Roll damage for a spell effect.

    Args:
        template: The spell effect template defining damage dice.
        slot_level: The level of the spell slot used.
        save_result: Optional saving throw result for half-damage effects.

    Returns:
        SpellDamageResult with damage total and breakdown.
    """
    dice_str = calculate_spell_dice(template, slot_level)
    if not dice_str:
        return SpellDamageResult(
            total=0,
            dice_rolled=[],
            damage_type=template.damage_type or "",
        )

    dice = DiceString(dice_str)
    total, dice_rolled = dice.roll_keeping_individual()

    # Apply save-for-half if applicable
    halved = False
    if (
        save_result
        and save_result.success
        and template.save_effect == SpellSaveEffect.HALF_DAMAGE
    ):
        total = total // 2
        halved = True

    return SpellDamageResult(
        total=total,
        dice_rolled=dice_rolled,
        damage_type=template.damage_type or "",
        halved=halved,
    )


def resolve_spell_healing(
    template: SpellEffectTemplate,
    slot_level: int,
    caster: Character,
) -> SpellHealingResult:
    """Roll healing for a spell effect.

    Args:
        template: The spell effect template defining healing dice.
        slot_level: The level of the spell slot used.
        caster: The character casting the spell (for ability modifier).

    Returns:
        SpellHealingResult with healing total and breakdown.
    """
    dice_str = calculate_spell_dice(template, slot_level)
    if not dice_str:
        return SpellHealingResult(total=0, dice_rolled=[])

    dice = DiceString(dice_str)
    modifier = get_spellcasting_ability_modifier(caster)
    total, dice_rolled = dice.roll_keeping_individual()
    total += modifier

    # Ensure healing is at least 0
    total = max(0, total)

    return SpellHealingResult(
        total=total,
        dice_rolled=dice_rolled,
    )


def resolve_spell_condition(
    template: SpellEffectTemplate,
    save_result: SpellSaveResult | None = None,
) -> SpellConditionResult | None:
    """Resolve a condition effect from a spell.

    Args:
        template: The spell effect template with condition.
        save_result: Optional saving throw result.

    Returns:
        SpellConditionResult if a condition is defined, None otherwise.
    """
    if not template.condition:
        return None

    # Condition is negated if save succeeds (for negates type)
    applied = True
    if (
        save_result
        and save_result.success
        and template.save_effect == SpellSaveEffect.NEGATES
    ):
        applied = False

    duration_rounds = None
    if template.duration_type == EffectDurationType.ROUNDS:
        duration_rounds = template.duration_value

    return SpellConditionResult(
        condition=template.condition,
        applied=applied,
        duration_rounds=duration_rounds,
    )


def resolve_spell_buff(
    template: SpellEffectTemplate,
) -> SpellBuffResult:
    """Resolve a buff/debuff effect from a spell.

    Args:
        template: The spell effect template with buff/debuff modifiers.

    Returns:
        SpellBuffResult with the effect modifiers.
    """
    duration_rounds = None
    if template.duration_type == EffectDurationType.ROUNDS:
        duration_rounds = template.duration_value

    return SpellBuffResult(
        description=template.buff_description,
        ac_modifier=template.ac_modifier,
        attack_modifier=template.attack_modifier,
        damage_modifier=template.damage_modifier,
        duration_rounds=duration_rounds,
    )


def resolve_spell(
    caster: Character,
    spell: SpellSettings,
    targets: list[Character],
    slot_level: int,
) -> SpellCastResult:
    """Resolve all effects of a spell cast.

    This is the main entry point for spell resolution. It processes
    all effect templates attached to the spell and generates results
    for each target.

    Args:
        caster: The character casting the spell.
        spell: The spell being cast.
        targets: List of characters targeted by the spell.
        slot_level: The level of spell slot used.

    Returns:
        SpellCastResult containing all effect results.
    """
    result = SpellCastResult(
        spell=spell,
        caster=caster,
        targets=targets,
        slot_level=slot_level,
        success=True,
    )

    # Get spell save DC for this caster
    dc = get_spell_save_dc(caster)

    # Track if this spell requires concentration
    requires_concentration = spell.concentration

    # Process each effect template
    for template in spell.effect_templates.all():
        for target in targets:
            # Resolve saving throw if required
            save_result = None
            if template.save_type != SpellSaveType.NONE:
                save_result = resolve_saving_throw(
                    target=target,
                    save_type=template.save_type,
                    dc=dc,
                )
                result.save_results.append((target, save_result))

                # If save negates and save was successful, skip this effect
                if (
                    save_result.success
                    and template.save_effect == SpellSaveEffect.NEGATES
                ):
                    continue

            # Resolve effect based on type
            if template.effect_type == SpellEffectType.DAMAGE:
                damage_result = resolve_spell_damage(
                    template=template,
                    slot_level=slot_level,
                    save_result=save_result,
                )
                result.damage_results.append((target, damage_result))

            elif template.effect_type == SpellEffectType.HEALING:
                healing_result = resolve_spell_healing(
                    template=template,
                    slot_level=slot_level,
                    caster=caster,
                )
                result.healing_results.append((target, healing_result))

            elif template.effect_type == SpellEffectType.CONDITION:
                condition_result = resolve_spell_condition(
                    template=template,
                    save_result=save_result,
                )
                if condition_result:
                    result.condition_results.append((target, condition_result))

            elif template.effect_type in (SpellEffectType.BUFF, SpellEffectType.DEBUFF):
                buff_result = resolve_spell_buff(template)
                result.buff_results.append((target, buff_result))

    # Mark if concentration started
    if requires_concentration and result.success:
        result.concentration_started = True

    return result


def apply_spell_damage(target: Character, result: SpellDamageResult) -> int:
    """Apply damage to target, respecting HP floor of 0.

    Args:
        target: The character taking damage.
        result: The damage result to apply.

    Returns:
        The target's remaining HP after damage.
    """
    target.hp = max(0, target.hp - result.total)
    target.save()
    return target.hp


def apply_spell_healing(target: Character, result: SpellHealingResult) -> int:
    """Apply healing to target, respecting HP max.

    Args:
        target: The character receiving healing.
        result: The healing result to apply.

    Returns:
        The target's new HP after healing.
    """
    old_hp = target.hp
    target.hp = min(target.max_hp, target.hp + result.total)
    target.save()

    # Calculate overheal
    result.overheal = max(0, result.total - (target.hp - old_hp))
    return target.hp


def apply_spell_condition(
    target: Character,
    result: SpellConditionResult,
) -> CharacterCondition | None:
    """Apply condition to target if successful.

    Args:
        target: The character receiving the condition.
        result: The condition result to apply.

    Returns:
        The CharacterCondition instance if applied, None otherwise.
    """
    if not result.applied:
        return None

    # Create or update the character condition
    char_condition, _ = CharacterCondition.objects.get_or_create(
        character=target,
        condition=result.condition,
    )
    return char_condition


def apply_spell_buff(
    target: Character,
    result: SpellBuffResult,
    template: SpellEffectTemplate,
    caster: Character,
) -> ActiveSpellEffect:
    """Create active spell effect for buff/debuff.

    Args:
        target: The character receiving the buff/debuff.
        result: The buff result with modifiers.
        template: The spell effect template.
        caster: The character who cast the spell.

    Returns:
        The created ActiveSpellEffect instance.
    """
    is_concentration = template.duration_type == EffectDurationType.CONCENTRATION

    return ActiveSpellEffect.objects.create(
        character=target,
        template=template,
        caster=caster,
        rounds_remaining=result.duration_rounds,
        is_concentration=is_concentration,
    )


def apply_spell_result(result: SpellCastResult) -> None:
    """Apply all effects from a spell cast result.

    This applies damage, healing, conditions, and buffs to all targets.
    Call this after resolve_spell() to actually modify game state.

    Args:
        result: The complete spell cast result to apply.
    """
    # Apply damage
    for target, damage_result in result.damage_results:
        apply_spell_damage(target, damage_result)

    # Apply healing
    for target, healing_result in result.healing_results:
        apply_spell_healing(target, healing_result)

    # Apply conditions
    for target, condition_result in result.condition_results:
        apply_spell_condition(target, condition_result)

    # Apply buffs/debuffs
    for target, buff_result in result.buff_results:
        # Find the template that generated this buff
        for template in result.spell.effect_templates.all():
            if template.effect_type in (SpellEffectType.BUFF, SpellEffectType.DEBUFF):
                apply_spell_buff(target, buff_result, template, result.caster)
                break

    # Start concentration if needed
    if result.concentration_started:
        from character.models import Concentration

        Concentration.start_concentration(
            character=result.caster,
            spell=result.spell,
        )
