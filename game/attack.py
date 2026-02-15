"""Attack resolution system for D&D 5e combat.

This module implements the core attack mechanics:
- Attack roll = d20 + ability modifier + proficiency (if proficient)
- Compare to target AC
- On hit, roll damage dice + ability modifier
- Critical hits on natural 20 (double damage dice)
- Critical misses on natural 1 (always miss)
- Weapon mastery effects (SRD 5.2.1)
"""

from dataclasses import dataclass, field

from character.constants.abilities import AbilityName
from character.models.character import Character
from equipment.constants.equipment import WeaponProperty, WeaponType
from equipment.models.equipment import Weapon
from character.models.proficiencies import WeaponProficiency
from utils.dice import DiceString

from .mastery import MasteryEffect, resolve_mastery


@dataclass
class AttackResult:
    """Result of an attack resolution."""

    # Attack roll details
    attack_roll: int
    natural_roll: int
    attack_modifier: int

    # Hit determination
    target_ac: int
    is_hit: bool
    is_critical_hit: bool
    is_critical_miss: bool

    # Damage (only populated on hit, or graze damage on miss)
    damage: int
    damage_dice: str
    damage_modifier: int

    # Metadata
    attacker_name: str
    target_name: str
    weapon_name: str
    ability_used: str

    # Weapon mastery effect
    mastery_effect: MasteryEffect = field(default_factory=MasteryEffect)

    # UI display data
    damage_rolls: list[int] = field(default_factory=list)
    second_natural_roll: int | None = (
        None  # Discarded d20 roll (advantage/disadvantage)
    )


def get_attack_ability(weapon: Weapon, attacker: Character) -> str:
    """Determine which ability to use for an attack roll.

    Args:
        weapon: The weapon being used.
        attacker: The character making the attack.

    Returns:
        The ability name (STR or DEX) to use for the attack.

    Rules:
        - Melee weapons use Strength by default
        - Ranged weapons use Dexterity
        - Finesse weapons can use either (picks the higher modifier)
        - Thrown weapons use Strength for melee range, Dexterity for thrown
    """
    properties = weapon.settings.properties or ""
    weapon_type = weapon.settings.weapon_type

    is_ranged = weapon_type in (WeaponType.SIMPLE_RANGED, WeaponType.MARTIAL_RANGED)
    is_finesse = WeaponProperty.FINESSE in properties

    if is_finesse:
        # Finesse weapons can use either STR or DEX - pick the higher one
        str_mod = attacker.strength.modifier
        dex_mod = attacker.dexterity.modifier
        if dex_mod >= str_mod:
            return str(AbilityName.DEXTERITY)
        return str(AbilityName.STRENGTH)

    if is_ranged:
        return str(AbilityName.DEXTERITY)

    # Default to Strength for melee weapons
    return str(AbilityName.STRENGTH)


def is_proficient_with_weapon(character: Character, weapon: Weapon) -> bool:
    """Check if a character is proficient with a weapon.

    Args:
        character: The character to check.
        weapon: The weapon to check proficiency for.

    Returns:
        True if the character is proficient with the weapon.
    """
    return WeaponProficiency.objects.filter(
        character=character, weapon=weapon.settings
    ).exists()


def resolve_attack(
    attacker: Character,
    target: Character,
    weapon: Weapon,
    advantage: bool = False,
    disadvantage: bool = False,
    use_mastery: bool = False,
) -> AttackResult:
    """Resolve a weapon attack against a target.

    Implements D&D 5e attack resolution:
    1. Roll d20 + ability modifier + proficiency bonus (if proficient)
    2. Compare to target AC
    3. On hit, roll damage dice + ability modifier
    4. Critical hit on natural 20 doubles damage dice
    5. Critical miss on natural 1 always misses
    6. Apply weapon mastery effects if character has mastered the weapon

    Args:
        attacker: The character making the attack.
        target: The character being attacked.
        weapon: The weapon being used.
        advantage: Whether the attacker has advantage on the roll.
        disadvantage: Whether the attacker has disadvantage on the roll.
        use_mastery: Whether to apply weapon mastery effects.

    Returns:
        AttackResult containing all details of the attack resolution.
    """
    # Determine which ability to use
    ability_name = get_attack_ability(weapon, attacker)
    ability = attacker.abilities.get(ability_type__name=ability_name)
    ability_modifier = ability.modifier

    # Calculate attack modifier
    proficiency_bonus = 0
    if is_proficient_with_weapon(attacker, weapon):
        proficiency_bonus = attacker.proficiency_bonus

    attack_modifier = ability_modifier + proficiency_bonus

    # Roll the attack
    d20 = DiceString("d20")
    second_natural_roll = None

    if advantage and disadvantage:
        # Cancel out - single roll
        _, rolls = d20.roll_keeping_individual()
        natural_roll = rolls[0]
    elif advantage:
        _, roll1, roll2 = d20.roll_with_advantage()
        natural_roll = max(roll1, roll2)
        second_natural_roll = min(roll1, roll2)
    elif disadvantage:
        _, roll1, roll2 = d20.roll_with_disadvantage()
        natural_roll = min(roll1, roll2)
        second_natural_roll = max(roll1, roll2)
    else:
        _, rolls = d20.roll_keeping_individual()
        natural_roll = rolls[0]

    attack_roll = natural_roll + attack_modifier
    is_nat_20 = natural_roll == 20
    is_nat_1 = natural_roll == 1

    # Determine hit/miss
    # Natural 1 always misses, natural 20 always hits
    is_critical_miss = is_nat_1
    is_critical_hit = is_nat_20

    if is_critical_miss:
        is_hit = False
    elif is_critical_hit:
        is_hit = True
    else:
        is_hit = attack_roll >= target.ac

    # Roll damage if hit
    damage = 0
    damage_dice = weapon.settings.damage or "1d4"  # Default to 1d4 if no damage set
    damage_modifier = ability_modifier
    damage_rolls: list[int] = []

    if is_hit:
        dice = DiceString(damage_dice)
        _, damage_rolls = dice.roll_keeping_individual()
        if is_critical_hit:
            _, crit_rolls = dice.roll_keeping_individual()
            damage_rolls = damage_rolls + crit_rolls
        damage = sum(damage_rolls) + damage_modifier
        # Ensure damage is at least 0 (negative modifiers can't reduce below 0)
        damage = max(0, damage)

    # Calculate target HP after damage for mastery effects
    target_hp_after = target.hp - damage if is_hit else target.hp

    # Resolve mastery effects
    mastery_effect = MasteryEffect()
    if use_mastery and weapon.settings.mastery:
        mastery_effect = resolve_mastery(
            mastery=weapon.settings.mastery,
            is_hit=is_hit,
            ability_modifier=ability_modifier,
            attacker_proficiency=attacker.proficiency_bonus,
            damage_dealt=damage,
            target_hp_remaining=target_hp_after,
        )
        # Apply graze damage on miss
        if mastery_effect.graze_damage > 0 and not is_hit:
            damage = mastery_effect.graze_damage

    return AttackResult(
        attack_roll=attack_roll,
        natural_roll=natural_roll,
        attack_modifier=attack_modifier,
        target_ac=target.ac,
        is_hit=is_hit,
        is_critical_hit=is_critical_hit,
        is_critical_miss=is_critical_miss,
        damage=damage,
        damage_dice=damage_dice,
        damage_modifier=damage_modifier,
        attacker_name=attacker.name,
        target_name=target.name,
        weapon_name=str(weapon.settings.name),
        ability_used=ability_name,
        mastery_effect=mastery_effect,
        damage_rolls=damage_rolls,
        second_natural_roll=second_natural_roll,
    )


def apply_damage(target: Character, damage: int) -> int:
    """Apply damage to a target character.

    Delegates to Character.take_damage() which handles temp HP absorption,
    death save counter resets, and damage <= 0 guards.

    Args:
        target: The character taking damage.
        damage: The amount of damage to apply.

    Returns:
        The target's remaining HP after damage.
    """
    target.take_damage(damage)
    target.refresh_from_db()
    return target.hp
