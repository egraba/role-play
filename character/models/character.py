from django.conf import settings
from django.db import models
from django.db.models.functions import Upper
from django.urls import reverse

from game.constants.events import Against, RollType
from utils.dice import DiceString

from ..constants.abilities import AbilityName
from ..constants.backgrounds import Background
from ..constants.character import Gender
from ..constants.races import Size
from .abilities import Ability
from .advancement import Advancement
from equipment.models.equipment import Inventory
from .classes import Class
from .races import Language
from .skills import Skill


class Character(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    species = models.ForeignKey(
        "character.Species", on_delete=models.PROTECT, null=True
    )
    height = models.FloatField(default=0)
    weight = models.SmallIntegerField(default=0)
    level = models.SmallIntegerField(default=1)
    xp = models.IntegerField(default=0)
    hp = models.SmallIntegerField(default=100)
    max_hp = models.SmallIntegerField(default=100)
    temp_hp = models.PositiveSmallIntegerField(default=0)
    death_save_successes = models.PositiveSmallIntegerField(default=0)
    death_save_failures = models.PositiveSmallIntegerField(default=0)
    skills = models.ManyToManyField(Skill)
    abilities = models.ManyToManyField(Ability)
    feats = models.ManyToManyField(
        "character.Feat", through="character.CharacterFeat", blank=True
    )
    classes = models.ManyToManyField(
        Class, through="character.CharacterClass", related_name="characters"
    )
    gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.MALE)
    ac = models.SmallIntegerField(default=0)
    size = models.CharField(max_length=1, choices=Size.choices, null=True, blank=True)
    speed = models.SmallIntegerField(null=True, blank=True)
    darkvision = models.PositiveIntegerField(default=0)  # Range in feet, 0 = none
    languages = models.ManyToManyField(Language)
    hit_dice = models.CharField(max_length=5, default="1d8")
    hp_increase = models.SmallIntegerField(default=0)
    background = models.CharField(max_length=10, choices=Background.choices)
    personality_trait = models.TextField(max_length=150)
    ideal = models.TextField(max_length=150, null=True, blank=True)
    bond = models.TextField(max_length=150, null=True, blank=True)
    flaw = models.TextField(max_length=150, null=True, blank=True)
    inventory = models.OneToOneField(
        Inventory, on_delete=models.CASCADE, blank=True, null=True
    )
    location = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        indexes = [
            models.Index(Upper("name"), name="character_name_upper_idx"),
        ]

    def __str__(self):
        return str(self.name)

    @property
    def strength(self):
        return self.abilities.get(ability_type__name=AbilityName.STRENGTH)

    @property
    def dexterity(self):
        return self.abilities.get(ability_type__name=AbilityName.DEXTERITY)

    @property
    def constitution(self):
        return self.abilities.get(ability_type__name=AbilityName.CONSTITUTION)

    @property
    def intelligence(self):
        return self.abilities.get(ability_type__name=AbilityName.INTELLIGENCE)

    @property
    def wisdom(self):
        return self.abilities.get(ability_type__name=AbilityName.WISDOM)

    @property
    def charisma(self):
        return self.abilities.get(ability_type__name=AbilityName.CHARISMA)

    @property
    def proficiency_bonus(self):
        """Calculate proficiency bonus based on character level.

        D&D 5e progression: levels 1-4 = +2, 5-8 = +3, 9-12 = +4, 13-16 = +5, 17-20 = +6.
        """
        return (self.level - 1) // 4 + 2

    @property
    def primary_class(self) -> Class | None:
        """Return the character's primary class."""
        char_class = self.character_classes.filter(is_primary=True).first()
        return char_class.klass if char_class else None

    @property
    def class_level(self) -> int:
        """Return level in primary class."""
        char_class = self.character_classes.filter(is_primary=True).first()
        return char_class.level if char_class else 0

    def get_absolute_url(self):
        return reverse("character-detail", args=(self.id,))

    def _check_level_increase(self):
        next_level = self.level + 1
        advancement = Advancement.objects.get(level=next_level)
        if self.xp >= advancement.xp:
            return True
        return False

    def _increase_level(self):
        self.level += 1

        # Increase hit dice
        self.hit_dice = DiceString(self.hit_dice).add_throws(1)

        # Increase HP
        self.max_hp += self.hp_increase

    def increase_xp(self, xp):
        self.xp += xp
        while self._check_level_increase():
            self._increase_level()

    def is_proficient(self, ability: Ability) -> bool:
        if not self.abilities.filter(ability_type=ability.ability_type).exists():
            return False
        return any(
            proficiency["ability_type_id"] == ability.ability_type.name
            for proficiency in self.savingthrowproficiency_set.values()
        )

    def _has_trait(self, trait_name: str) -> bool:
        """Check if character's species has a specific trait."""
        if not self.species:
            return False
        return self.species.traits.filter(name=trait_name).exists()

    def has_feat(self, feat_name: str) -> bool:
        """Check if character has a specific feat."""
        return self.feats.filter(name=feat_name).exists()

    def has_advantage(self, roll_type: RollType, against: Against) -> bool:
        if (
            self._has_trait("dwarven_resilience")
            and roll_type == RollType.SAVING_THROW
            and against == Against.POISON
        ):
            return True
        if (
            self._has_trait("fey_ancestry")
            and roll_type == RollType.SAVING_THROW
            and against == Against.CHARM
        ):
            return True
        if (
            self._has_trait("brave")
            and roll_type == RollType.SAVING_THROW
            and against == Against.BEING_FRIGHTENED
        ):
            return True
        return False

    def has_disadvantage(self, roll_type: RollType, against: Against) -> bool:
        # Not supported.
        return False

    @property
    def is_unconscious(self) -> bool:
        """Check if character is at 0 HP."""
        return self.hp <= 0

    @property
    def is_dead(self) -> bool:
        """Check if character has failed 3 death saves."""
        return self.death_save_failures >= 3

    @property
    def is_stable(self) -> bool:
        """Check if character has succeeded 3 death saves."""
        return self.death_save_successes >= 3

    @property
    def effective_hp(self) -> int:
        """Return total effective HP including temporary HP."""
        return self.hp + self.temp_hp

    @property
    def hp_percentage(self) -> int:
        """Return HP as percentage of max HP."""
        if self.max_hp <= 0:
            return 0
        return min(100, max(0, int((self.hp / self.max_hp) * 100)))

    def take_damage(self, damage: int) -> int:
        """Apply damage to character, consuming temp HP first.

        Returns the actual damage taken (after temp HP absorption).
        """
        if damage <= 0:
            return 0

        actual_damage = damage

        # Temp HP absorbs damage first
        if self.temp_hp > 0:
            if self.temp_hp >= damage:
                self.temp_hp -= damage
                self.save()
                return 0  # All damage absorbed by temp HP
            else:
                damage -= self.temp_hp
                self.temp_hp = 0

        # Apply remaining damage to HP
        self.hp = max(0, self.hp - damage)

        # Reset death saves if dropping to 0 HP
        if self.hp == 0:
            self.death_save_successes = 0
            self.death_save_failures = 0

        self.save()
        return actual_damage

    def heal(self, amount: int) -> int:
        """Heal character up to max HP.

        Returns the actual amount healed.
        """
        if amount <= 0:
            return 0

        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)

        # Reset death saves when healed from 0
        if old_hp == 0 and self.hp > 0:
            self.death_save_successes = 0
            self.death_save_failures = 0

        self.save()
        return self.hp - old_hp

    def add_temp_hp(self, amount: int) -> None:
        """Add temporary HP. Takes the higher value if already has temp HP."""
        if amount > self.temp_hp:
            self.temp_hp = amount
            self.save()

    def remove_temp_hp(self) -> None:
        """Remove all temporary HP."""
        self.temp_hp = 0
        self.save()

    def add_death_save_success(self) -> bool:
        """Record a death save success. Returns True if now stable."""
        if self.death_save_successes < 3:
            self.death_save_successes += 1
            self.save()
        return self.is_stable

    def add_death_save_failure(self) -> bool:
        """Record a death save failure. Returns True if now dead."""
        if self.death_save_failures < 3:
            self.death_save_failures += 1
            self.save()
        return self.is_dead

    def reset_death_saves(self) -> None:
        """Reset death save counters."""
        self.death_save_successes = 0
        self.death_save_failures = 0
        self.save()
