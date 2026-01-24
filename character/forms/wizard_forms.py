"""
Character creation wizard forms.

7-step wizard forms for comprehensive character creation:
1. Species Selection
2. Class Selection
3. Ability Scores
4. Background Selection
5. Skills Selection
6. Equipment Selection
7. Review & Confirm
"""

from django import forms

from ..constants.abilities import AbilityScore
from ..constants.backgrounds import BACKGROUNDS, Background
from ..constants.classes import ClassName
from ..constants.skills import SkillName
from ..models.character import Character
from ..models.classes import Class
from ..models.feats import Feat
from ..models.species import Species
from .equipment_choices_providers import (
    ClericEquipmentChoicesProvider,
    FighterEquipmentChoicesProvider,
    RogueEquipmentChoicesProvider,
    WizardEquipmentChoicesProvider,
)
from .mixins import NoDuplicateValuesFormMixin

# Common widget classes
DROPDOWN_ATTRS = {"class": "rpgui-dropdown"}


class SpeciesSelectForm(forms.Form):
    """Step 1: Species selection with racial trait preview data."""

    species = forms.ModelChoiceField(
        queryset=Species.objects.all().prefetch_related("traits", "languages"),
        widget=forms.Select(attrs=DROPDOWN_ATTRS),
        label="Species",
        empty_label="---------",
    )

    def get_species_preview_data(self):
        """Return preview data for all species for JavaScript rendering."""
        preview_data = {}
        for species in Species.objects.all().prefetch_related("traits", "languages"):
            preview_data[species.name] = {
                "display_name": species.get_name_display(),
                "size": species.get_size_display(),
                "speed": species.speed,
                "darkvision": species.darkvision,
                "description": species.description,
                "traits": [
                    {"name": trait.get_name_display(), "description": trait.description}
                    for trait in species.traits.all()
                ],
                "languages": [
                    lang.get_name_display() for lang in species.languages.all()
                ],
            }
        return preview_data


class ClassSelectForm(forms.Form):
    """Step 2: Class selection with starting features preview."""

    klass = forms.ModelChoiceField(
        queryset=Class.objects.all()
        .select_related("primary_ability")
        .prefetch_related("saving_throws", "features"),
        widget=forms.Select(attrs=DROPDOWN_ATTRS),
        label="Class",
        empty_label="---------",
    )

    def get_class_preview_data(self):
        """Return preview data for all classes for JavaScript rendering."""
        # Map armor proficiency codes to display names
        armor_display = {
            "LA": "Light Armor",
            "MA": "Medium Armor",
            "HA": "Heavy Armor",
            "SH": "Shields",
        }
        weapon_display = {
            "simple": "Simple Weapons",
            "martial": "Martial Weapons",
        }

        preview_data = {}
        for klass in (
            Class.objects.all()
            .select_related("primary_ability")
            .prefetch_related("saving_throws", "features")
        ):
            level_1_features = klass.features.filter(level=1)
            preview_data[klass.name] = {
                "display_name": klass.get_name_display(),
                "description": klass.description,
                "hit_die": f"d{klass.hit_die}",
                "hp_first_level": klass.hp_first_level,
                "primary_ability": klass.primary_ability.get_name_display(),
                "saving_throws": [
                    st.get_name_display() for st in klass.saving_throws.all()
                ],
                "armor_proficiencies": [
                    armor_display.get(p, p) for p in klass.armor_proficiencies
                ],
                "weapon_proficiencies": [
                    weapon_display.get(p, p) for p in klass.weapon_proficiencies
                ],
                "level_1_features": [
                    {"name": f.name, "description": f.description}
                    for f in level_1_features
                ],
            }
        return preview_data


class AbilityScoreForm(NoDuplicateValuesFormMixin, forms.Form):
    """
    Step 3: Ability score generation.

    Supports three methods:
    1. Standard Array (15, 14, 13, 12, 10, 8)
    2. Point Buy (27 points, costs vary)
    3. Roll (4d6 drop lowest) - values passed from JS
    """

    EMPTY_CHOICE = ("", "---------")

    # Only check ability score fields for duplicates, not generation_method
    duplicate_check_fields = [
        "strength",
        "dexterity",
        "constitution",
        "intelligence",
        "wisdom",
        "charisma",
    ]

    GENERATION_METHODS = [
        ("standard", "Standard Array (15, 14, 13, 12, 10, 8)"),
        ("point_buy", "Point Buy (27 points)"),
        ("roll", "Roll (4d6 drop lowest)"),
    ]

    # Point costs for point buy system
    POINT_COSTS = {
        8: 0,
        9: 1,
        10: 2,
        11: 3,
        12: 4,
        13: 5,
        14: 7,
        15: 9,
    }

    generation_method = forms.ChoiceField(
        choices=GENERATION_METHODS,
        widget=forms.RadioSelect(attrs={"class": "generation-method-radio"}),
        initial="standard",
        label="Generation Method",
    )

    strength = forms.TypedChoiceField(
        choices=[EMPTY_CHOICE, *AbilityScore.choices],
        coerce=int,
        widget=forms.Select(attrs=DROPDOWN_ATTRS),
        label="Strength",
    )
    dexterity = forms.TypedChoiceField(
        choices=[EMPTY_CHOICE, *AbilityScore.choices],
        coerce=int,
        widget=forms.Select(attrs=DROPDOWN_ATTRS),
        label="Dexterity",
    )
    constitution = forms.TypedChoiceField(
        choices=[EMPTY_CHOICE, *AbilityScore.choices],
        coerce=int,
        widget=forms.Select(attrs=DROPDOWN_ATTRS),
        label="Constitution",
    )
    intelligence = forms.TypedChoiceField(
        choices=[EMPTY_CHOICE, *AbilityScore.choices],
        coerce=int,
        widget=forms.Select(attrs=DROPDOWN_ATTRS),
        label="Intelligence",
    )
    wisdom = forms.TypedChoiceField(
        choices=[EMPTY_CHOICE, *AbilityScore.choices],
        coerce=int,
        widget=forms.Select(attrs=DROPDOWN_ATTRS),
        label="Wisdom",
    )
    charisma = forms.TypedChoiceField(
        choices=[EMPTY_CHOICE, *AbilityScore.choices],
        coerce=int,
        widget=forms.Select(attrs=DROPDOWN_ATTRS),
        label="Charisma",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        method = self.data.get("2-generation_method") or self.initial.get(
            "generation_method", "standard"
        )

        if method == "point_buy":
            # For point buy, allow scores 8-15
            point_buy_choices = [self.EMPTY_CHOICE] + [
                (score, str(score)) for score in range(8, 16)
            ]
            for field in [
                "strength",
                "dexterity",
                "constitution",
                "intelligence",
                "wisdom",
                "charisma",
            ]:
                self.fields[field].choices = point_buy_choices
        elif method == "roll":
            # For roll, allow any score 3-18
            roll_choices = [self.EMPTY_CHOICE] + [
                (score, str(score)) for score in range(3, 19)
            ]
            for field in [
                "strength",
                "dexterity",
                "constitution",
                "intelligence",
                "wisdom",
                "charisma",
            ]:
                self.fields[field].choices = roll_choices

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get("generation_method")

        if method == "point_buy":
            # Validate point buy total
            total_points = 0
            for field in [
                "strength",
                "dexterity",
                "constitution",
                "intelligence",
                "wisdom",
                "charisma",
            ]:
                score = cleaned_data.get(field)
                if score:
                    total_points += self.POINT_COSTS.get(score, 0)

            if total_points > 27:
                raise forms.ValidationError(
                    f"Point buy total ({total_points}) exceeds 27 points."
                )

        return cleaned_data


class BackgroundSelectForm(forms.Form):
    """Step 4: Background selection with skills and feat preview."""

    background = forms.ChoiceField(
        choices=[("", "---------")] + list(Background.choices),
        widget=forms.Select(attrs=DROPDOWN_ATTRS),
        label="Background",
    )

    def get_background_preview_data(self):
        """Return preview data for all backgrounds for JavaScript rendering."""
        preview_data = {}
        for bg_value, bg_display in Background.choices:
            bg_data = BACKGROUNDS.get(bg_value, {})
            skill_profs = bg_data.get("skill_proficiencies", set())
            tool_prof = bg_data.get("tool_proficiency")
            origin_feat_name = bg_data.get("origin_feat")

            # Get feat description if available
            feat_info = None
            if origin_feat_name:
                try:
                    feat = Feat.objects.get(name=origin_feat_name)
                    feat_info = {
                        "name": feat.get_name_display(),
                        "description": feat.description,
                    }
                except Feat.DoesNotExist:
                    feat_info = {"name": origin_feat_name, "description": ""}

            preview_data[bg_value] = {
                "display_name": bg_display,
                "skill_proficiencies": [SkillName(s).label for s in skill_profs],
                "tool_proficiency": tool_prof.label if tool_prof else None,
                "origin_feat": feat_info,
                "personality_traits": list(
                    bg_data.get("personality_traits", {}).values()
                ),
                "ideals": list(bg_data.get("ideals", {}).values()),
                "bonds": list(bg_data.get("bonds", {}).values()),
                "flaws": list(bg_data.get("flaws", {}).values()),
            }
        return preview_data


def _get_skills(class_name: str) -> set[tuple[str, str]] | None:
    """Return available skills for a given class."""
    from utils.converters import duplicate_choice

    match class_name:
        case ClassName.CLERIC:
            return {
                duplicate_choice(SkillName.HISTORY),
                duplicate_choice(SkillName.INSIGHT),
                duplicate_choice(SkillName.MEDICINE),
                duplicate_choice(SkillName.PERSUASION),
                duplicate_choice(SkillName.RELIGION),
            }
        case ClassName.FIGHTER:
            return {
                duplicate_choice(SkillName.ACROBATICS),
                duplicate_choice(SkillName.ANIMAL_HANDLING),
                duplicate_choice(SkillName.ATHLETICS),
                duplicate_choice(SkillName.HISTORY),
                duplicate_choice(SkillName.INSIGHT),
                duplicate_choice(SkillName.INTIMIDATION),
                duplicate_choice(SkillName.PERCEPTION),
                duplicate_choice(SkillName.SURVIVAL),
            }
        case ClassName.ROGUE:
            return {
                duplicate_choice(SkillName.ACROBATICS),
                duplicate_choice(SkillName.ATHLETICS),
                duplicate_choice(SkillName.DECEPTION),
                duplicate_choice(SkillName.INSIGHT),
                duplicate_choice(SkillName.INTIMIDATION),
                duplicate_choice(SkillName.INVESTIGATION),
                duplicate_choice(SkillName.PERCEPTION),
                duplicate_choice(SkillName.PERFORMANCE),
                duplicate_choice(SkillName.PERSUASION),
                duplicate_choice(SkillName.SLEIGHT_OF_HAND),
                duplicate_choice(SkillName.STEALTH),
            }
        case ClassName.WIZARD:
            return {
                duplicate_choice(SkillName.ARCANA),
                duplicate_choice(SkillName.HISTORY),
                duplicate_choice(SkillName.INSIGHT),
                duplicate_choice(SkillName.INVESTIGATION),
                duplicate_choice(SkillName.MEDICINE),
                duplicate_choice(SkillName.RELIGION),
            }
        case _:
            return None


def _get_num_skills(class_name: str) -> int:
    """Return the number of skills a class can choose."""
    match class_name:
        case ClassName.ROGUE:
            return 4
        case ClassName.BARD:
            return 3
        case _:
            return 2


class SkillsSelectForm(NoDuplicateValuesFormMixin, forms.Form):
    """Step 5: Class-specific skill selection."""

    EMPTY_CHOICE = ("", "---------")

    def _get_choices(self, choices):
        """Return choices with empty choice prepended, or None if no choices."""
        return [self.EMPTY_CHOICE, *choices] if choices else None

    def _add_field_if_choices(self, field_name, choices, label=None):
        """Add field only if there are choices available."""
        if choices:
            self.fields[field_name] = forms.ChoiceField(
                choices=choices,
                widget=forms.Select(attrs=DROPDOWN_ATTRS),
                label=label,
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        klass = self.initial.get("klass")
        if not klass:
            return

        # klass can be a Class model instance or a ClassName enum/string value
        class_name = klass.name if hasattr(klass, "_meta") else klass
        choices = self._get_choices(_get_skills(class_name))
        num_skills = _get_num_skills(class_name)

        skill_labels = ["First Skill", "Second Skill", "Third Skill", "Fourth Skill"]
        skill_fields = ["first_skill", "second_skill", "third_skill", "fourth_skill"]

        for i in range(num_skills):
            self._add_field_if_choices(skill_fields[i], choices, skill_labels[i])

    def get_skill_descriptions(self):
        """Return skill descriptions for preview."""
        from ..models.skills import Skill

        skill_data = {}
        for skill in Skill.objects.all().select_related("ability_type"):
            skill_data[skill.name] = {
                "display_name": skill.get_name_display(),
                "ability": skill.ability_type.get_name_display(),
                "description": skill.description,
            }
        return skill_data


class EquipmentSelectForm(forms.Form):
    """Step 6: Class-specific equipment selection."""

    EMPTY_CHOICE = ("", "---------")

    def _get_choices(self, choices):
        """Return choices with empty choice prepended, or None if no choices."""
        return [self.EMPTY_CHOICE, *choices] if choices else None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        klass = self.initial.get("klass")
        if not klass:
            return

        # klass can be a Class model instance or a ClassName enum/string value
        class_name = klass.name if hasattr(klass, "_meta") else klass

        match class_name:
            case ClassName.CLERIC:
                choices_provider = ClericEquipmentChoicesProvider()
                fields = ["first_weapon", "second_weapon", "armor", "gear", "pack"]
            case ClassName.FIGHTER:
                choices_provider = FighterEquipmentChoicesProvider()
                fields = ["first_weapon", "second_weapon", "third_weapon", "pack"]
            case ClassName.ROGUE:
                choices_provider = RogueEquipmentChoicesProvider()
                fields = ["first_weapon", "second_weapon", "pack"]
            case ClassName.WIZARD:
                choices_provider = WizardEquipmentChoicesProvider()
                fields = ["first_weapon", "gear", "pack"]
            case _:
                # For classes without specific equipment choices, no fields are added
                return

        # Field labels for better UX
        field_labels = {
            "first_weapon": "Primary Weapon",
            "second_weapon": "Secondary Weapon",
            "third_weapon": "Tertiary Weapon",
            "armor": "Armor",
            "gear": "Gear",
            "pack": "Equipment Pack",
        }

        field_choices = {
            "first_weapon": self._get_choices(
                choices_provider.get_first_weapon_choices()
            ),
            "second_weapon": self._get_choices(
                choices_provider.get_second_weapon_choices()
            ),
            "third_weapon": self._get_choices(
                choices_provider.get_third_weapon_choices()
            ),
            "armor": self._get_choices(choices_provider.get_armor_choices()),
            "gear": self._get_choices(choices_provider.get_gear_choices()),
            "pack": self._get_choices(choices_provider.get_pack_choices()),
        }

        for field in fields:
            choices = field_choices[field]
            if choices:
                self.fields[field] = forms.ChoiceField(
                    choices=choices,
                    widget=forms.Select(attrs=DROPDOWN_ATTRS),
                    label=field_labels.get(field, field.replace("_", " ").title()),
                )


class ReviewForm(forms.Form):
    """Step 7: Final review and character name."""

    name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={"class": "rpg-input", "placeholder": "Enter character name"}
        ),
        label="Character Name",
    )

    def __init__(self, *args, **kwargs):
        self.wizard_data = kwargs.pop("wizard_data", {})
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data["name"]
        if Character.objects.filter(name=name).exists():
            raise forms.ValidationError(
                "A character with this name already exists. Please choose a different name."
            )
        return name

    def get_character_summary(self):
        """Build a summary of the character from all wizard steps."""
        summary = {}

        # Species (from step 0)
        species_data = self.wizard_data.get("0", {})
        if species_data and "species" in species_data:
            species_pk = species_data.get("0-species") or species_data.get("species")
            try:
                species = Species.objects.get(pk=species_pk)
                summary["species"] = {
                    "name": species.get_name_display(),
                    "size": species.get_size_display(),
                    "speed": species.speed,
                    "darkvision": species.darkvision,
                }
            except Species.DoesNotExist:
                pass

        # Class (from step 1)
        class_data = self.wizard_data.get("1", {})
        if class_data:
            klass_pk = class_data.get("1-klass") or class_data.get("klass")
            try:
                klass = Class.objects.get(pk=klass_pk)
                summary["klass"] = {
                    "name": klass.get_name_display(),
                    "hit_die": f"d{klass.hit_die}",
                    "hp_first_level": klass.hp_first_level,
                }
            except Class.DoesNotExist:
                pass

        # Abilities (from step 2)
        abilities_data = self.wizard_data.get("2", {})
        if abilities_data:
            summary["abilities"] = {
                "strength": abilities_data.get("2-strength")
                or abilities_data.get("strength"),
                "dexterity": abilities_data.get("2-dexterity")
                or abilities_data.get("dexterity"),
                "constitution": abilities_data.get("2-constitution")
                or abilities_data.get("constitution"),
                "intelligence": abilities_data.get("2-intelligence")
                or abilities_data.get("intelligence"),
                "wisdom": abilities_data.get("2-wisdom")
                or abilities_data.get("wisdom"),
                "charisma": abilities_data.get("2-charisma")
                or abilities_data.get("charisma"),
            }

        # Background (from step 3)
        bg_data = self.wizard_data.get("3", {})
        if bg_data:
            bg_value = bg_data.get("3-background") or bg_data.get("background")
            if bg_value:
                for choice_value, choice_label in Background.choices:
                    if choice_value == bg_value:
                        summary["background"] = choice_label
                        break

        # Skills (from step 4)
        skills_data = self.wizard_data.get("4", {})
        if skills_data:
            skills = []
            for key, value in skills_data.items():
                if "skill" in key and value:
                    # Convert skill name to display
                    try:
                        skills.append(SkillName(value).label)
                    except ValueError:
                        skills.append(value)
            summary["skills"] = skills

        # Equipment (from step 5)
        equipment_data = self.wizard_data.get("5", {})
        if equipment_data:
            equipment = []
            for key, value in equipment_data.items():
                if value and not key.startswith("csrfmiddleware"):
                    equipment.append(value)
            summary["equipment"] = equipment

        return summary
