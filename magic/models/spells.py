from django.db import models

from character.constants.classes import ClassName
from magic.constants.spells import (
    CasterType,
    CastingTime,
    SpellDuration,
    SpellLevel,
    SpellRange,
    SpellSchool,
    SpellcastingAbility,
)


class SpellSettings(models.Model):
    """D&D 5e spell data (the spell definition, not a character's copy)."""

    name = models.CharField(max_length=100, primary_key=True)
    level = models.PositiveSmallIntegerField(choices=SpellLevel.choices)
    school = models.CharField(max_length=15, choices=SpellSchool.choices)
    casting_time = models.CharField(max_length=15, choices=CastingTime.choices)
    casting_time_detail = models.CharField(
        max_length=100,
        blank=True,
        help_text="Additional casting time info (e.g., reaction trigger)",
    )
    range = models.CharField(max_length=15, choices=SpellRange.choices)
    range_detail = models.CharField(
        max_length=50,
        blank=True,
        help_text="Additional range info (e.g., area of effect)",
    )
    components = models.JSONField(default=list, help_text="List of components: V, S, M")
    material_components = models.CharField(
        max_length=500,
        blank=True,
        help_text="Description of material components if any",
    )
    material_cost = models.PositiveIntegerField(
        default=0, help_text="GP cost of material components (0 if no cost)"
    )
    material_consumed = models.BooleanField(
        default=False, help_text="Whether material components are consumed"
    )
    duration = models.CharField(max_length=20, choices=SpellDuration.choices)
    concentration = models.BooleanField(default=False)
    ritual = models.BooleanField(default=False)
    description = models.TextField(max_length=5000)
    higher_levels = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Effect when cast at higher levels",
    )
    classes = models.JSONField(
        default=list, help_text="List of class names that can learn this spell"
    )

    class Meta:
        db_table = "character_spellsettings"
        ordering = ["level", "name"]
        verbose_name_plural = "spell settings"

    def __str__(self) -> str:
        level_display = "Cantrip" if self.level == 0 else f"Level {self.level}"
        return f"{self.name} ({level_display})"

    @property
    def is_cantrip(self) -> bool:
        return self.level == SpellLevel.CANTRIP


class Spell(models.Model):
    """A spell known by a character (for spontaneous casters like Sorcerer, Bard)."""

    character = models.ForeignKey(
        "character.Character", on_delete=models.CASCADE, related_name="spells_known"
    )
    settings = models.ForeignKey(SpellSettings, on_delete=models.CASCADE)
    source = models.CharField(
        max_length=50,
        blank=True,
        help_text="Source of the spell (e.g., class, feat, item)",
    )

    class Meta:
        db_table = "character_spell"
        unique_together = ["character", "settings"]
        ordering = ["settings__level", "settings__name"]

    def __str__(self) -> str:
        return f"{self.character.name}: {self.settings.name}"


class SpellPreparation(models.Model):
    """A spell prepared by a character (for prepared casters like Cleric, Wizard)."""

    character = models.ForeignKey(
        "character.Character", on_delete=models.CASCADE, related_name="prepared_spells"
    )
    settings = models.ForeignKey(SpellSettings, on_delete=models.CASCADE)
    always_prepared = models.BooleanField(
        default=False, help_text="Domain/subclass spells that don't count against limit"
    )

    class Meta:
        db_table = "character_spellpreparation"
        unique_together = ["character", "settings"]
        ordering = ["settings__level", "settings__name"]

    def __str__(self) -> str:
        return f"{self.character.name}: {self.settings.name} (prepared)"


class SpellSlotTable(models.Model):
    """Spell slots available per class level (reference data)."""

    class_name = models.CharField(max_length=20, choices=ClassName.choices)
    class_level = models.PositiveSmallIntegerField()
    slot_level = models.PositiveSmallIntegerField(
        choices=[(i, f"{i}") for i in range(1, 10)]
    )
    slots = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "character_spellslottable"
        unique_together = ["class_name", "class_level", "slot_level"]
        ordering = ["class_name", "class_level", "slot_level"]
        verbose_name_plural = "spell slot tables"

    def __str__(self) -> str:
        return (
            f"{self.class_name} L{self.class_level}: {self.slots}x L{self.slot_level}"
        )


class CharacterSpellSlot(models.Model):
    """Tracks a character's spell slots and usage."""

    character = models.ForeignKey(
        "character.Character", on_delete=models.CASCADE, related_name="spell_slots"
    )
    slot_level = models.PositiveSmallIntegerField(
        choices=[(i, f"Level {i}") for i in range(1, 10)]
    )
    total = models.PositiveSmallIntegerField(default=0)
    used = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "character_characterspellslot"
        unique_together = ["character", "slot_level"]
        ordering = ["character", "slot_level"]

    def __str__(self) -> str:
        return (
            f"{self.character.name}: L{self.slot_level} ({self.remaining}/{self.total})"
        )

    @property
    def remaining(self) -> int:
        return self.total - self.used

    def use_slot(self) -> bool:
        """Use a spell slot. Returns True if successful, False if no slots remaining."""
        if self.remaining > 0:
            self.used += 1
            self.save()
            return True
        return False

    def restore_slot(self, count: int = 1) -> None:
        """Restore spell slots (e.g., from Arcane Recovery)."""
        self.used = max(0, self.used - count)
        self.save()

    def restore_all(self) -> None:
        """Restore all spell slots (long rest)."""
        self.used = 0
        self.save()


class WarlockSpellSlot(models.Model):
    """Special spell slot tracking for Warlock's Pact Magic."""

    character = models.OneToOneField(
        "character.Character", on_delete=models.CASCADE, related_name="pact_magic"
    )
    slot_level = models.PositiveSmallIntegerField(default=1)
    total = models.PositiveSmallIntegerField(default=1)
    used = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "character_warlockspellslot"

    def __str__(self) -> str:
        return f"{self.character.name}: Pact Magic L{self.slot_level} ({self.remaining}/{self.total})"

    @property
    def remaining(self) -> int:
        return self.total - self.used

    def use_slot(self) -> bool:
        """Use a pact magic slot. Returns True if successful."""
        if self.remaining > 0:
            self.used += 1
            self.save()
            return True
        return False

    def restore_all(self) -> None:
        """Restore all pact magic slots (short rest)."""
        self.used = 0
        self.save()


class ClassSpellcasting(models.Model):
    """Spellcasting configuration per class."""

    klass = models.OneToOneField(
        "character.Class", on_delete=models.CASCADE, related_name="spellcasting"
    )
    caster_type = models.CharField(
        max_length=10,
        choices=CasterType.choices,
        blank=True,
        help_text="Empty for non-casters",
    )
    spellcasting_ability = models.CharField(
        max_length=15,
        choices=SpellcastingAbility.choices,
        blank=True,
    )
    learns_cantrips = models.BooleanField(default=False)
    spell_list_access = models.BooleanField(
        default=False,
        help_text="True if class has access to full class spell list (prepared casters)",
    )
    ritual_casting = models.BooleanField(default=False)
    spellcasting_focus = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of focus (arcane, druidic, holy symbol)",
    )

    class Meta:
        db_table = "character_classspellcasting"
        verbose_name_plural = "class spellcasting"

    def __str__(self) -> str:
        if not self.caster_type:
            return f"{self.klass.name}: Non-caster"
        return f"{self.klass.name}: {self.caster_type} ({self.spellcasting_ability})"

    @property
    def is_caster(self) -> bool:
        return bool(self.caster_type)


class Concentration(models.Model):
    """Tracks a character's active concentration spell."""

    character = models.OneToOneField(
        "character.Character", on_delete=models.CASCADE, related_name="concentration"
    )
    spell = models.ForeignKey(
        SpellSettings, on_delete=models.CASCADE, related_name="active_concentrations"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    rounds_remaining = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Rounds remaining if duration is measured in rounds",
    )

    class Meta:
        db_table = "character_concentration"

    def __str__(self) -> str:
        return f"{self.character.name} concentrating on {self.spell.name}"

    def break_concentration(self) -> None:
        """End concentration on the spell."""
        self.delete()

    @classmethod
    def start_concentration(
        cls, character, spell: SpellSettings, rounds: int | None = None
    ) -> "Concentration":
        """Start concentrating on a spell. Breaks existing concentration if any."""
        # Break existing concentration first
        cls.objects.filter(character=character).delete()

        return cls.objects.create(
            character=character,
            spell=spell,
            rounds_remaining=rounds,
        )
