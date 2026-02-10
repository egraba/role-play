"""Weapon mastery system for D&D 5e SRD 5.2.1.

This module implements weapon mastery properties that provide special
effects when a character has mastered a weapon.

Mastery Properties:
- Cleave: On kill, excess damage carries to another enemy within 5 feet
- Graze: On miss, deal ability modifier damage (minimum 0)
- Nick: Can make extra attack with light weapon as part of Attack action
- Push: On hit, push target 10 feet away (if Large or smaller)
- Sap: On hit, target has disadvantage on next attack
- Slow: On hit, reduce target's speed by 10 feet
- Topple: On hit, target must make CON save or be knocked prone
- Vex: On hit, gain advantage on next attack against same target
"""

from dataclasses import dataclass, field

from equipment.constants.equipment import WeaponMastery


@dataclass
class MasteryEffect:
    """Represents the effect of a weapon mastery property.

    This dataclass captures what happened as a result of a mastery property
    being applied during an attack.
    """

    mastery: str | None = None
    triggered: bool = False
    description: str = ""

    # Graze effect
    graze_damage: int = 0

    # Cleave effect
    cleave_damage_available: int = 0

    # Push effect
    push_distance: int = 0

    # Slow effect
    speed_reduction: int = 0

    # Status effects applied to target
    target_has_disadvantage: bool = False  # Sap
    target_knocked_prone: bool = False  # Topple (requires save)
    topple_save_dc: int = 0

    # Status effects applied to attacker
    attacker_has_advantage_on_next: bool = False  # Vex
    attacker_can_nick: bool = False  # Nick

    # Additional targets affected
    additional_targets: list[str] = field(default_factory=list)


def get_mastery_save_dc(attacker_proficiency: int, ability_modifier: int) -> int:
    """Calculate the save DC for mastery effects that require saves.

    DC = 8 + proficiency bonus + ability modifier used for the attack.

    Args:
        attacker_proficiency: The attacker's proficiency bonus.
        ability_modifier: The ability modifier used for the attack.

    Returns:
        The save DC for mastery effects.
    """
    return 8 + attacker_proficiency + ability_modifier


def resolve_mastery_on_hit(
    mastery: str | None,
    ability_modifier: int,
    attacker_proficiency: int,
    damage_dealt: int,
    target_hp_remaining: int,
) -> MasteryEffect:
    """Resolve mastery effects that trigger on a hit.

    Args:
        mastery: The weapon's mastery property (or None).
        ability_modifier: The ability modifier used for the attack.
        attacker_proficiency: The attacker's proficiency bonus.
        damage_dealt: The damage dealt by the attack.
        target_hp_remaining: The target's HP after damage.

    Returns:
        MasteryEffect describing what happened.
    """
    if not mastery:
        return MasteryEffect()

    effect = MasteryEffect(mastery=mastery, triggered=True)

    if mastery == WeaponMastery.CLEAVE:
        # Cleave: If attack kills target, excess damage can hit another enemy
        if target_hp_remaining <= 0:
            # Target was killed, calculate excess damage
            # excess = damage - (damage needed to reach 0)
            # Since target_hp_remaining = old_hp - damage, and it's <= 0
            # The excess is abs(target_hp_remaining)
            effect.cleave_damage_available = abs(target_hp_remaining)
            effect.description = (
                f"Cleave: {effect.cleave_damage_available} excess damage "
                "can hit another enemy within 5 feet"
            )

    elif mastery == WeaponMastery.PUSH:
        # Push: Target is pushed 10 feet away (if Large or smaller)
        effect.push_distance = 10
        effect.description = "Push: Target is pushed 10 feet away"

    elif mastery == WeaponMastery.SAP:
        # Sap: Target has disadvantage on next attack
        effect.target_has_disadvantage = True
        effect.description = (
            "Sap: Target has disadvantage on its next attack "
            "before your next turn starts"
        )

    elif mastery == WeaponMastery.SLOW:
        # Slow: Target's speed is reduced by 10 feet
        effect.speed_reduction = 10
        effect.description = (
            "Slow: Target's speed is reduced by 10 feet "
            "until the start of your next turn"
        )

    elif mastery == WeaponMastery.TOPPLE:
        # Topple: Target must make CON save or be knocked prone
        effect.topple_save_dc = get_mastery_save_dc(
            attacker_proficiency, ability_modifier
        )
        effect.description = (
            f"Topple: Target must make DC {effect.topple_save_dc} Constitution "
            "save or be knocked prone"
        )

    elif mastery == WeaponMastery.VEX:
        # Vex: Attacker has advantage on next attack against same target
        effect.attacker_has_advantage_on_next = True
        effect.description = (
            "Vex: You have advantage on your next attack roll "
            "against this target before the end of this turn"
        )

    elif mastery == WeaponMastery.NICK:
        # Nick: Can make extra attack with light weapon
        effect.attacker_can_nick = True
        effect.description = (
            "Nick: You can make an extra attack with a light weapon "
            "as part of this Attack action"
        )

    else:
        # Graze doesn't trigger on hit - only on miss
        effect.triggered = False

    return effect


def resolve_mastery_on_miss(
    mastery: str | None,
    ability_modifier: int,
) -> MasteryEffect:
    """Resolve mastery effects that trigger on a miss.

    Args:
        mastery: The weapon's mastery property (or None).
        ability_modifier: The ability modifier used for the attack.

    Returns:
        MasteryEffect describing what happened.
    """
    if not mastery:
        return MasteryEffect()

    effect = MasteryEffect(mastery=mastery)

    if mastery == WeaponMastery.GRAZE:
        # Graze: Deal ability modifier damage on miss (minimum 0)
        effect.triggered = True
        effect.graze_damage = max(0, ability_modifier)
        if effect.graze_damage > 0:
            effect.description = f"Graze: Deal {effect.graze_damage} damage on miss"
        else:
            effect.description = "Graze: No damage (modifier is 0 or negative)"

    return effect


def resolve_mastery(
    mastery: str | None,
    is_hit: bool,
    ability_modifier: int,
    attacker_proficiency: int,
    damage_dealt: int = 0,
    target_hp_remaining: int = 0,
) -> MasteryEffect:
    """Resolve weapon mastery effects based on attack outcome.

    Args:
        mastery: The weapon's mastery property (or None).
        is_hit: Whether the attack hit.
        ability_modifier: The ability modifier used for the attack.
        attacker_proficiency: The attacker's proficiency bonus.
        damage_dealt: The damage dealt by the attack (if hit).
        target_hp_remaining: The target's HP after damage (if hit).

    Returns:
        MasteryEffect describing what happened.
    """
    if is_hit:
        return resolve_mastery_on_hit(
            mastery=mastery,
            ability_modifier=ability_modifier,
            attacker_proficiency=attacker_proficiency,
            damage_dealt=damage_dealt,
            target_hp_remaining=target_hp_remaining,
        )
    else:
        return resolve_mastery_on_miss(
            mastery=mastery,
            ability_modifier=ability_modifier,
        )
