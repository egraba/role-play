from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db.models.functions import Upper
from django.urls import reverse

from game.constants.events import Against, RollType
from utils.dice import Dice

from ..constants.backgrounds import Background
from ..constants.character import Gender
from ..constants.races import Alignment, Race, SenseName, Size
from ..utils.cache import advancement_key
from .abilities import Ability
from .advancement import Advancement
from .equipment import Inventory
from .klasses import Klass
from .races import Language, Sense
from .skills import Skill


class Character(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    race = models.CharField(max_length=14, choices=Race.choices)
    height = models.FloatField(default=0)
    weight = models.SmallIntegerField(default=0)
    klass = models.CharField(max_length=1, choices=Klass.choices, verbose_name="class")
    level = models.SmallIntegerField(default=1)
    xp = models.IntegerField(default=0)
    hp = models.SmallIntegerField(default=100)
    max_hp = models.SmallIntegerField(default=100)
    proficiency_bonus = models.SmallIntegerField(default=2)
    skills = models.ManyToManyField(Skill)
    abilities = models.ManyToManyField(Ability)
    gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.MALE)
    ac = models.SmallIntegerField(default=0)
    adult_age = models.SmallIntegerField(null=True, blank=True)
    life_expectancy = models.SmallIntegerField(null=True, blank=True)
    alignment = models.CharField(
        max_length=1, choices=Alignment.choices, null=True, blank=True
    )
    size = models.CharField(max_length=1, choices=Size.choices, null=True, blank=True)
    speed = models.SmallIntegerField(null=True, blank=True)
    languages = models.ManyToManyField(Language)
    senses = models.ManyToManyField(Sense)
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

    class Meta:
        indexes = [
            models.Index(Upper("name"), name="character_name_upper_idx"),
        ]

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("character-detail", args=(self.id,))

    def _check_level_increase(self):
        next_level = self.level + 1
        advancement = cache.get_or_set(
            advancement_key(next_level), Advancement.objects.get(level=next_level)
        )
        if self.xp >= advancement.xp:
            return True
        return False

    def _increase_level(self):
        self.level += 1
        advancement = cache.get_or_set(
            advancement_key(self.level), Advancement.objects.get(level=self.level)
        )
        self.proficiency_bonus += advancement.proficiency_bonus

        # Increase hit dice
        self.hit_dice = Dice(self.hit_dice).add_throws(1)

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

    def has_advantage(self, roll_type: RollType, against: Against) -> bool:
        has_dwarven_resilience = bool(
            self.senses.filter(name=SenseName.DWARVEN_RESILIENCE)
        )
        has_fey_ancestry = bool(self.senses.filter(name=SenseName.FEY_ANCESTRY))
        is_brave = bool(self.senses.filter(name=SenseName.BRAVE))

        if (
            has_dwarven_resilience
            and roll_type == RollType.SAVING_THROW
            and against == Against.POISON
        ):
            return True
        if has_fey_ancestry and RollType.SAVING_THROW and against == Against.CHARM:
            return True
        if is_brave and RollType.SAVING_THROW and against == Against.BEING_FRIGHTENED:
            return True
        return False

    def has_disadvantage(self, roll_type: RollType, against: Against) -> bool:
        # Not supported.
        return False
