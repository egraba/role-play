"""
Monster models for D&D 5e SRD.

This module implements the monster system including:
- MonsterSettings: Reference data for monster stat blocks
- Monster: Concrete monster instances (for combat encounters)
- MonsterAction: Actions available to monsters
- MonsterTrait: Special traits and abilities
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from character.ability_modifiers import compute_ability_modifier
from bestiary.constants.monsters import (
    ActionType,
    Alignment,
    AreaShape,
    ChallengeRating,
    CR_XP_TABLE,
    CreatureSize,
    CreatureType,
    DamageType,
    MonsterName,
    RechargeType,
    SaveEffect,
    SaveType,
)


class MonsterSettings(models.Model):
    """
    Reference data for monster stat blocks from D&D 5e SRD.

    This model stores the complete stat block template for each monster type.
    Individual instances in combat are stored in Monster.
    """

    # Basic Information
    name = models.CharField(
        max_length=50, choices=MonsterName.choices, primary_key=True
    )
    size = models.CharField(max_length=15, choices=CreatureSize.choices)
    creature_type = models.CharField(max_length=15, choices=CreatureType.choices)
    subtype = models.CharField(
        max_length=50,
        blank=True,
        help_text="E.g., 'shapechanger', 'devil', 'goblinoid'",
    )
    alignment = models.CharField(max_length=5, choices=Alignment.choices)
    description = models.TextField(max_length=2000, blank=True)

    # Armor Class
    ac = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    ac_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="E.g., 'natural armor', 'plate armor'",
    )

    # Hit Points
    hit_dice = models.CharField(
        max_length=20,
        help_text="E.g., '8d8+16' for a creature with 8 HD and +2 CON",
    )
    hp_average = models.PositiveSmallIntegerField(
        help_text="Average HP (used for quick reference)",
    )

    # Speed (stored as JSON for multiple movement types)
    # Example: {"walk": 30, "fly": 60, "swim": 30}
    speed = models.JSONField(
        default=dict,
        help_text="Movement speeds by type (e.g., {'walk': 30, 'fly': 60})",
    )

    # Ability Scores
    strength = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    dexterity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    constitution = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    intelligence = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    wisdom = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    charisma = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )

    # Saving Throw Proficiencies (stored as JSON)
    # Example: {"STR": 5, "CON": 7} - stores the total bonus
    saving_throws = models.JSONField(
        default=dict,
        blank=True,
        help_text="Saving throw bonuses (e.g., {'STR': 5, 'CON': 7})",
    )

    # Skills (stored as JSON)
    # Example: {"perception": 5, "stealth": 6}
    skills = models.JSONField(
        default=dict,
        blank=True,
        help_text="Skill bonuses (e.g., {'perception': 5, 'stealth': 6})",
    )

    # Damage Resistances, Immunities, Vulnerabilities (stored as JSON arrays)
    damage_vulnerabilities = models.JSONField(
        default=list,
        blank=True,
        help_text="List of damage types the creature is vulnerable to",
    )
    damage_resistances = models.JSONField(
        default=list,
        blank=True,
        help_text="List of damage types the creature resists",
    )
    damage_immunities = models.JSONField(
        default=list,
        blank=True,
        help_text="List of damage types the creature is immune to",
    )

    # Condition Immunities (stored as JSON array)
    condition_immunities = models.JSONField(
        default=list,
        blank=True,
        help_text="List of conditions the creature is immune to",
    )

    # Senses (stored as JSON)
    # Example: {"darkvision": 60, "blindsight": 30, "passive_perception": 14}
    senses = models.JSONField(
        default=dict,
        help_text="Senses (e.g., {'darkvision': 60, 'passive_perception': 14})",
    )

    # Languages (stored as JSON array or string)
    languages = models.JSONField(
        default=list,
        blank=True,
        help_text="Languages the creature speaks/understands",
    )
    telepathy = models.PositiveSmallIntegerField(
        default=0,
        help_text="Telepathy range in feet (0 if none)",
    )

    # Challenge Rating
    challenge_rating = models.CharField(
        max_length=5,
        choices=ChallengeRating.choices,
    )

    # Proficiency Bonus (derived from CR)
    proficiency_bonus = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2), MaxValueValidator(9)],
        help_text="Proficiency bonus based on CR",
    )

    # Special Traits (stored as JSON for flexibility)
    # Example: [{"name": "Keen Senses", "description": "Advantage on Perception checks..."}]
    traits = models.JSONField(
        default=list,
        blank=True,
        help_text="Special traits as list of {name, description} objects",
    )

    # Actions (stored as JSON for flexibility)
    # Example: [{"name": "Bite", "description": "Melee Weapon Attack: +5 to hit..."}]
    actions = models.JSONField(
        default=list,
        blank=True,
        help_text="Actions as list of {name, description} objects",
    )

    # Reactions (stored as JSON)
    reactions = models.JSONField(
        default=list,
        blank=True,
        help_text="Reactions as list of {name, description} objects",
    )

    # Legendary Actions (for legendary creatures)
    legendary_actions = models.JSONField(
        default=list,
        blank=True,
        help_text="Legendary actions as list of {name, description, cost} objects",
    )
    legendary_action_count = models.PositiveSmallIntegerField(
        default=0,
        help_text="Number of legendary actions per round (typically 3)",
    )

    # Lair Actions (for creatures with lairs)
    lair_actions = models.JSONField(
        default=list,
        blank=True,
        help_text="Lair actions as list of {description} objects",
    )
    has_lair = models.BooleanField(default=False)

    # Spellcasting (optional, stored as JSON for flexibility)
    # Example: {"ability": "INT", "save_dc": 15, "attack_bonus": 7,
    #           "spells": {"cantrips": [...], "1st": [...], ...}}
    spellcasting = models.JSONField(
        default=dict,
        blank=True,
        help_text="Spellcasting details if the creature is a spellcaster",
    )

    class Meta:
        db_table = "character_monstersettings"
        ordering = ["name"]
        verbose_name = "monster settings"
        verbose_name_plural = "monster settings"

    def __str__(self):
        return f"{self.name} (CR {self.challenge_rating})"

    @property
    def xp(self) -> int:
        """Get XP value based on challenge rating."""
        return CR_XP_TABLE.get(self.challenge_rating, 0)

    @property
    def strength_modifier(self) -> int:
        """Calculate Strength modifier."""
        return compute_ability_modifier(self.strength)

    @property
    def dexterity_modifier(self) -> int:
        """Calculate Dexterity modifier."""
        return compute_ability_modifier(self.dexterity)

    @property
    def constitution_modifier(self) -> int:
        """Calculate Constitution modifier."""
        return compute_ability_modifier(self.constitution)

    @property
    def intelligence_modifier(self) -> int:
        """Calculate Intelligence modifier."""
        return compute_ability_modifier(self.intelligence)

    @property
    def wisdom_modifier(self) -> int:
        """Calculate Wisdom modifier."""
        return compute_ability_modifier(self.wisdom)

    @property
    def charisma_modifier(self) -> int:
        """Calculate Charisma modifier."""
        return compute_ability_modifier(self.charisma)

    def get_saving_throw(self, ability: str) -> int:
        """
        Get the saving throw bonus for an ability.

        Returns the proficient bonus if the creature has it,
        otherwise returns the raw ability modifier.
        """
        if ability in self.saving_throws:
            return self.saving_throws[ability]

        # Map ability abbreviation to modifier
        ability_modifiers = {
            "STR": self.strength_modifier,
            "DEX": self.dexterity_modifier,
            "CON": self.constitution_modifier,
            "INT": self.intelligence_modifier,
            "WIS": self.wisdom_modifier,
            "CHA": self.charisma_modifier,
        }
        return ability_modifiers.get(ability, 0)

    def get_skill_bonus(self, skill: str) -> int:
        """Get the bonus for a skill check."""
        return self.skills.get(skill.lower(), 0)

    def is_immune_to_damage(self, damage_type: str) -> bool:
        """Check if creature is immune to a damage type."""
        return damage_type.lower() in [d.lower() for d in self.damage_immunities]

    def is_resistant_to_damage(self, damage_type: str) -> bool:
        """Check if creature is resistant to a damage type."""
        return damage_type.lower() in [d.lower() for d in self.damage_resistances]

    def is_vulnerable_to_damage(self, damage_type: str) -> bool:
        """Check if creature is vulnerable to a damage type."""
        return damage_type.lower() in [d.lower() for d in self.damage_vulnerabilities]

    def is_immune_to_condition(self, condition: str) -> bool:
        """Check if creature is immune to a condition."""
        return condition.lower() in [c.lower() for c in self.condition_immunities]


class Monster(models.Model):
    """
    A concrete monster instance in a combat encounter.

    This represents an individual monster that can take damage,
    be tracked in initiative, and have ongoing effects.
    """

    settings = models.ForeignKey(
        MonsterSettings,
        on_delete=models.CASCADE,
        related_name="instances",
    )

    # Instance-specific name (e.g., "Goblin 1", "Boss Troll")
    instance_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name for this specific instance",
    )

    # Current HP tracking
    hp_current = models.SmallIntegerField()
    hp_max = models.PositiveSmallIntegerField()
    hp_temp = models.PositiveSmallIntegerField(default=0)

    # Combat tracking
    combat = models.ForeignKey(
        "game.Combat",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="monsters",
    )

    # For legendary creatures
    legendary_actions_remaining = models.PositiveSmallIntegerField(default=0)

    # Notes for this specific instance
    notes = models.TextField(max_length=500, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "character_monster"
        ordering = ["settings__name", "instance_name"]
        verbose_name = "monster"
        verbose_name_plural = "monsters"

    def __str__(self):
        if self.instance_name:
            return f"{self.instance_name} ({self.settings.name})"
        return str(self.settings.name)

    def save(self, *args, **kwargs):
        # Initialize HP from settings if not set
        if not self.pk:
            if not self.hp_max:
                self.hp_max = self.settings.hp_average
            if self.hp_current is None:
                self.hp_current = self.hp_max
            if self.settings.legendary_action_count > 0:
                self.legendary_actions_remaining = self.settings.legendary_action_count
        super().save(*args, **kwargs)

    @property
    def is_alive(self) -> bool:
        """Check if the monster is still alive."""
        return self.hp_current > 0

    @property
    def is_bloodied(self) -> bool:
        """Check if the monster is at or below half HP."""
        return self.hp_current <= self.hp_max // 2

    def take_damage(self, damage: int, damage_type: str = "") -> int:
        """
        Apply damage to the monster, considering resistances/immunities.

        Returns the actual damage taken after modifications.
        """
        actual_damage = damage

        if damage_type:
            if self.settings.is_immune_to_damage(damage_type):
                actual_damage = 0
            elif self.settings.is_resistant_to_damage(damage_type):
                actual_damage = damage // 2
            elif self.settings.is_vulnerable_to_damage(damage_type):
                actual_damage = damage * 2

        # Apply to temp HP first
        if self.hp_temp > 0:
            if actual_damage <= self.hp_temp:
                self.hp_temp -= actual_damage
                actual_damage = 0
            else:
                actual_damage -= self.hp_temp
                self.hp_temp = 0

        self.hp_current = max(0, self.hp_current - actual_damage)
        self.save()
        return actual_damage

    def heal(self, amount: int) -> int:
        """
        Heal the monster.

        Returns the actual amount healed.
        """
        old_hp = self.hp_current
        self.hp_current = min(self.hp_max, self.hp_current + amount)
        self.save()
        return self.hp_current - old_hp

    def add_temp_hp(self, amount: int) -> None:
        """Add temporary hit points (doesn't stack, takes higher)."""
        self.hp_temp = max(self.hp_temp, amount)
        self.save()

    def use_legendary_action(self, cost: int = 1) -> bool:
        """
        Use legendary actions.

        Returns True if successful, False if not enough actions remaining.
        """
        if self.legendary_actions_remaining < cost:
            return False
        self.legendary_actions_remaining -= cost
        self.save()
        return True

    def reset_legendary_actions(self) -> None:
        """Reset legendary actions at the start of the monster's turn."""
        self.legendary_actions_remaining = self.settings.legendary_action_count
        self.save()

    @classmethod
    def create_from_settings(
        cls,
        settings: MonsterSettings,
        instance_name: str = "",
        hp_override: int | None = None,
    ) -> "Monster":
        """
        Create a new monster instance from settings.

        Args:
            settings: The MonsterSettings to use
            instance_name: Optional name for this instance
            hp_override: Optional HP override (otherwise uses average)
        """
        hp = hp_override if hp_override is not None else settings.hp_average
        return cls.objects.create(
            settings=settings,
            instance_name=instance_name,
            hp_current=hp,
            hp_max=hp,
            legendary_actions_remaining=settings.legendary_action_count,
        )


class MonsterActionTemplate(models.Model):
    """
    Structured action template for monster abilities.

    This model provides structured data for monster actions including:
    - Melee/ranged weapon attacks with hit bonuses and damage
    - Melee/ranged spell attacks
    - Special abilities with saving throws
    - Area of effect abilities
    - Recharge mechanics
    """

    monster = models.ForeignKey(
        MonsterSettings,
        on_delete=models.CASCADE,
        related_name="action_templates",
    )

    # Basic action information
    name = models.CharField(max_length=100)
    action_type = models.CharField(
        max_length=20,
        choices=ActionType.choices,
        default=ActionType.SPECIAL,
    )
    description = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Full description text for the action",
    )

    # Attack properties (for weapon/spell attacks)
    attack_bonus = models.SmallIntegerField(
        null=True,
        blank=True,
        help_text="Bonus to attack roll (e.g., +5)",
    )
    reach = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Melee reach in feet",
    )
    range_normal = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Normal range in feet",
    )
    range_long = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Long range in feet (with disadvantage)",
    )
    targets = models.CharField(
        max_length=100,
        default="one target",
        help_text="Target description (e.g., 'one target', 'one creature')",
    )

    # Damage properties
    damage_dice = models.CharField(
        max_length=30,
        blank=True,
        help_text="Damage dice (e.g., '2d6+4')",
    )
    damage_type = models.CharField(
        max_length=20,
        choices=DamageType.choices,
        blank=True,
    )
    extra_damage_dice = models.CharField(
        max_length=30,
        blank=True,
        help_text="Additional damage dice (e.g., '1d6' poison)",
    )
    extra_damage_type = models.CharField(
        max_length=20,
        choices=DamageType.choices,
        blank=True,
    )
    versatile_damage = models.CharField(
        max_length=30,
        blank=True,
        help_text="Damage dice when used two-handed",
    )

    # Saving throw properties
    save_dc = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Saving throw DC",
    )
    save_type = models.CharField(
        max_length=5,
        choices=SaveType.choices,
        default=SaveType.NONE,
    )
    save_effect = models.CharField(
        max_length=20,
        choices=SaveEffect.choices,
        default=SaveEffect.NONE,
    )

    # Area of effect properties
    area_shape = models.CharField(
        max_length=15,
        choices=AreaShape.choices,
        default=AreaShape.NONE,
    )
    area_size = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Size of the area in feet",
    )

    # Recharge mechanics
    recharge = models.CharField(
        max_length=15,
        choices=RechargeType.choices,
        default=RechargeType.NONE,
    )

    # Additional effects (stored as JSON for flexibility)
    # E.g., conditions applied, movement restrictions, etc.
    effects = models.JSONField(
        default=list,
        blank=True,
        help_text="Additional effects as list of {type, description}",
    )

    # Ordering for display
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "character_monsteractiontemplate"
        ordering = ["monster", "sort_order", "name"]
        verbose_name = "monster action template"
        verbose_name_plural = "monster action templates"

    def __str__(self):
        return f"{self.monster.name}: {self.name}"

    @property
    def is_attack(self) -> bool:
        """Check if this action is an attack."""
        return self.action_type in [
            ActionType.MELEE_WEAPON,
            ActionType.RANGED_WEAPON,
            ActionType.MELEE_SPELL,
            ActionType.RANGED_SPELL,
        ]

    @property
    def requires_save(self) -> bool:
        """Check if this action requires a saving throw."""
        return self.save_type != SaveType.NONE and self.save_dc is not None

    @property
    def has_area_effect(self) -> bool:
        """Check if this action has an area of effect."""
        return self.area_shape != AreaShape.NONE

    def get_attack_description(self) -> str:
        """Generate formatted attack description."""
        if not self.is_attack:
            return ""

        attack_type = ActionType(self.action_type).label
        parts = [f"{attack_type}:"]

        if self.attack_bonus is not None:
            bonus_str = (
                f"+{self.attack_bonus}"
                if self.attack_bonus >= 0
                else str(self.attack_bonus)
            )
            parts.append(f"{bonus_str} to hit,")

        if self.reach:
            parts.append(f"reach {self.reach} ft.,")
        elif self.range_normal:
            if self.range_long:
                parts.append(f"range {self.range_normal}/{self.range_long} ft.,")
            else:
                parts.append(f"range {self.range_normal} ft.,")

        parts.append(f"{self.targets}.")

        return " ".join(parts)

    def get_damage_description(self) -> str:
        """Generate formatted damage description."""
        if not self.damage_dice:
            return ""

        parts = [f"Hit: {self.damage_dice}"]
        if self.damage_type:
            parts.append(f"{DamageType(self.damage_type).label.lower()} damage")

        if self.extra_damage_dice and self.extra_damage_type:
            parts.append(
                f"plus {self.extra_damage_dice} "
                f"{DamageType(self.extra_damage_type).label.lower()} damage"
            )

        return " ".join(parts) + "."


class MonsterMultiattack(models.Model):
    """
    Defines multiattack patterns for monsters.

    Specifies which actions can be combined in a multiattack
    and how many times each can be used.
    """

    monster = models.OneToOneField(
        MonsterSettings,
        on_delete=models.CASCADE,
        related_name="multiattack",
    )
    description = models.TextField(
        max_length=500,
        help_text="Text description of the multiattack",
    )

    class Meta:
        db_table = "character_monstermultiattack"
        verbose_name = "monster multiattack"
        verbose_name_plural = "monster multiattacks"

    def __str__(self):
        return f"{self.monster.name}: Multiattack"


class MultiattackAction(models.Model):
    """
    Individual action within a multiattack pattern.

    Links to action templates and specifies count.
    """

    multiattack = models.ForeignKey(
        MonsterMultiattack,
        on_delete=models.CASCADE,
        related_name="actions",
    )
    action = models.ForeignKey(
        MonsterActionTemplate,
        on_delete=models.CASCADE,
        related_name="multiattack_uses",
    )
    count = models.PositiveSmallIntegerField(
        default=1,
        help_text="Number of times this action is used in multiattack",
    )
    is_optional = models.BooleanField(
        default=False,
        help_text="Whether this action is optional (e.g., 'or' options)",
    )
    group = models.PositiveSmallIntegerField(
        default=0,
        help_text="Group number for 'or' options (same group = choose one)",
    )

    class Meta:
        db_table = "character_multiattackaction"
        ordering = ["multiattack", "group", "-count"]
        verbose_name = "multiattack action"
        verbose_name_plural = "multiattack actions"

    def __str__(self):
        return f"{self.multiattack.monster.name}: {self.count}x {self.action.name}"


class LegendaryActionTemplate(models.Model):
    """
    Structured legendary action for legendary creatures.

    Legendary actions can be taken at the end of another creature's turn,
    using a pool of legendary action points that refresh each round.
    """

    monster = models.ForeignKey(
        MonsterSettings,
        on_delete=models.CASCADE,
        related_name="legendary_action_templates",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    cost = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        help_text="Legendary action cost (1-3)",
    )

    # Link to an action template if this legendary action uses one
    action_template = models.ForeignKey(
        MonsterActionTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="legendary_uses",
        help_text="Link to action template if this uses an existing action",
    )

    # Ordering for display
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "character_legendaryactiontemplate"
        ordering = ["monster", "sort_order", "cost", "name"]
        verbose_name = "legendary action template"
        verbose_name_plural = "legendary action templates"

    def __str__(self):
        cost_str = f"(Costs {self.cost} Actions)" if self.cost > 1 else ""
        return f"{self.monster.name}: {self.name} {cost_str}".strip()


class LairActionTemplate(models.Model):
    """
    Structured lair action for creatures with lairs.

    Lair actions occur on initiative count 20 (losing ties)
    when the creature is in its lair.
    """

    monster = models.ForeignKey(
        MonsterSettings,
        on_delete=models.CASCADE,
        related_name="lair_action_templates",
    )
    description = models.TextField(max_length=500)

    # Saving throw if required
    save_dc = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )
    save_type = models.CharField(
        max_length=5,
        choices=SaveType.choices,
        default=SaveType.NONE,
    )
    save_effect = models.CharField(
        max_length=20,
        choices=SaveEffect.choices,
        default=SaveEffect.NONE,
    )

    # Area effect if applicable
    area_shape = models.CharField(
        max_length=15,
        choices=AreaShape.choices,
        default=AreaShape.NONE,
    )
    area_size = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    # Effects (stored as JSON)
    effects = models.JSONField(
        default=list,
        blank=True,
    )

    # Ordering for display
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "character_lairactiontemplate"
        ordering = ["monster", "sort_order"]
        verbose_name = "lair action template"
        verbose_name_plural = "lair action templates"

    def __str__(self):
        return f"{self.monster.name}: Lair Action {self.sort_order + 1}"


class MonsterTrait(models.Model):
    """
    Structured special trait for monsters.

    Traits are passive abilities that are always active,
    like Keen Senses, Pack Tactics, or Magic Resistance.
    """

    monster = models.ForeignKey(
        MonsterSettings,
        on_delete=models.CASCADE,
        related_name="trait_templates",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)

    # Some traits have limited uses
    uses_per_day = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Number of uses per day (null = unlimited)",
    )
    recharge = models.CharField(
        max_length=15,
        choices=RechargeType.choices,
        default=RechargeType.NONE,
    )

    # Ordering for display
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "character_monstertrait"
        ordering = ["monster", "sort_order", "name"]
        verbose_name = "monster trait"
        verbose_name_plural = "monster traits"

    def __str__(self):
        return f"{self.monster.name}: {self.name}"


class MonsterReaction(models.Model):
    """
    Structured reaction for monsters.

    Reactions are triggered by specific conditions and can be
    taken once per round, outside the monster's turn.
    """

    monster = models.ForeignKey(
        MonsterSettings,
        on_delete=models.CASCADE,
        related_name="reaction_templates",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    trigger = models.CharField(
        max_length=200,
        help_text="What triggers this reaction",
    )

    # Link to an action template if the reaction uses one
    action_template = models.ForeignKey(
        MonsterActionTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reaction_uses",
    )

    class Meta:
        db_table = "character_monsterreaction"
        ordering = ["monster", "name"]
        verbose_name = "monster reaction"
        verbose_name_plural = "monster reactions"

    def __str__(self):
        return f"{self.monster.name}: {self.name}"
