import json
import re
from enum import StrEnum

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic import DetailView
from formtools.wizard.views import SessionWizardView

from ..character_attributes_builders import (
    BackgroundBuilder,
    BaseBuilder,
    ClassBuilder,
    DerivedStatsBuilder,
    SpeciesBuilder,
    SpellcastingBuilder,
)
from equipment.constants.equipment import ArmorName, GearName, ToolName, WeaponName
from ..constants.classes import ClassName
from ..forms.wizard_forms import (
    AbilityScoreForm,
    BackgroundSelectForm,
    ClassSelectForm,
    EquipmentSelectForm,
    ReviewForm,
    SkillsSelectForm,
    SpeciesSelectForm,
)
from ..models.character import Character
from ..services import CharacterSheetService

MULTI_EQUIPMENT_REGEX = r"\S+\s&\s\S+"


class CharacterDetailView(LoginRequiredMixin, DetailView):
    model = Character
    template_name = "character/character.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character = self.object
        context.update(CharacterSheetService.get_character_sheet_data(character))
        return context


class CharacterCreateView(LoginRequiredMixin, SessionWizardView):
    """
    7-step character creation wizard.

    Steps:
    0. Species Selection
    1. Class Selection
    2. Ability Scores
    3. Background Selection
    4. Skills Selection
    5. Equipment Selection
    6. Review & Confirm
    """

    form_list = [
        SpeciesSelectForm,  # Step 0: Species
        ClassSelectForm,  # Step 1: Class
        AbilityScoreForm,  # Step 2: Abilities
        BackgroundSelectForm,  # Step 3: Background
        SkillsSelectForm,  # Step 4: Skills
        EquipmentSelectForm,  # Step 5: Equipment
        ReviewForm,  # Step 6: Review
    ]

    class Step(StrEnum):
        SPECIES_SELECTION = "0"
        CLASS_SELECTION = "1"
        ABILITY_SCORES = "2"
        BACKGROUND_SELECTION = "3"
        SKILLS_SELECTION = "4"
        EQUIPMENT_SELECTION = "5"
        REVIEW = "6"

    STEP_TITLES = {
        "0": "Species",
        "1": "Class",
        "2": "Abilities",
        "3": "Background",
        "4": "Skills",
        "5": "Equipment",
        "6": "Review",
    }

    def get_template_names(self):
        """Return step-specific template."""
        step = self.steps.current
        templates = {
            self.Step.SPECIES_SELECTION: "character/wizard/step_species.html",
            self.Step.CLASS_SELECTION: "character/wizard/step_class.html",
            self.Step.ABILITY_SCORES: "character/wizard/step_abilities.html",
            self.Step.BACKGROUND_SELECTION: "character/wizard/step_background.html",
            self.Step.SKILLS_SELECTION: "character/wizard/step_skills.html",
            self.Step.EQUIPMENT_SELECTION: "character/wizard/step_equipment.html",
            self.Step.REVIEW: "character/wizard/step_review.html",
        }
        return [templates.get(step, "character/wizard/base_wizard.html")]

    def get_form_initial(self, step):
        """Pass data from previous steps to inform current step."""
        initial = self.initial_dict.get(step, {})

        # Skills and Equipment need class from step 1
        if step in (self.Step.SKILLS_SELECTION, self.Step.EQUIPMENT_SELECTION):
            class_data = self.storage.get_step_data(self.Step.CLASS_SELECTION)
            if class_data:
                klass = class_data.get("1-klass")
                initial["klass"] = klass

        return initial

    def get_form_kwargs(self, step):
        """Pass wizard data to ReviewForm."""
        kwargs = super().get_form_kwargs(step)

        if step == self.Step.REVIEW:
            # Collect all previous step data for the review
            wizard_data = {}
            for prev_step in range(int(step)):
                step_data = self.storage.get_step_data(str(prev_step))
                if step_data:
                    wizard_data[str(prev_step)] = step_data
            kwargs["wizard_data"] = wizard_data

        return kwargs

    def get_context_data(self, form, **kwargs):
        """Add wizard navigation and preview data to context."""
        context = super().get_context_data(form=form, **kwargs)

        # Step information for progress indicator
        context["step_titles"] = self.STEP_TITLES
        context["current_step"] = self.steps.current
        context["current_step_title"] = self.STEP_TITLES.get(self.steps.current, "Step")

        # Add preview data for specific steps
        current_step = self.steps.current

        if current_step == self.Step.SPECIES_SELECTION:
            context["species_preview"] = json.dumps(form.get_species_preview_data())

        elif current_step == self.Step.CLASS_SELECTION:
            context["class_preview"] = json.dumps(form.get_class_preview_data())

        elif current_step == self.Step.BACKGROUND_SELECTION:
            context["background_preview"] = json.dumps(
                form.get_background_preview_data()
            )

        elif current_step == self.Step.SKILLS_SELECTION:
            context["skill_descriptions"] = json.dumps(form.get_skill_descriptions())
            # Pass class info for display
            class_data = self.storage.get_step_data(self.Step.CLASS_SELECTION)
            if class_data:
                from ..models.classes import Class

                klass_pk = class_data.get("1-klass")
                try:
                    klass = Class.objects.get(pk=klass_pk)
                    context["selected_class"] = klass.get_name_display()
                except Class.DoesNotExist:
                    pass

        elif current_step == self.Step.EQUIPMENT_SELECTION:
            # Pass class info for display
            class_data = self.storage.get_step_data(self.Step.CLASS_SELECTION)
            if class_data:
                from ..models.classes import Class

                klass_pk = class_data.get("1-klass")
                try:
                    klass = Class.objects.get(pk=klass_pk)
                    context["selected_class"] = klass.get_name_display()
                except Class.DoesNotExist:
                    pass

        elif current_step == self.Step.REVIEW:
            context["character_summary"] = form.get_character_summary()

        return context

    def done(self, form_list, **kwargs):
        """Process all forms and create the character."""
        forms_by_type = {type(f).__name__: f for f in form_list}

        # Extract data from each form
        species_form = forms_by_type.get("SpeciesSelectForm")
        class_form = forms_by_type.get("ClassSelectForm")
        ability_form = forms_by_type.get("AbilityScoreForm")
        background_form = forms_by_type.get("BackgroundSelectForm")
        skills_form = forms_by_type.get("SkillsSelectForm")
        equipment_form = forms_by_type.get("EquipmentSelectForm")
        review_form = forms_by_type.get("ReviewForm")

        # Create character with name from review step
        character = Character(
            user=self.request.user,
            name=review_form.cleaned_data["name"],
            species=species_form.cleaned_data["species"],
            background=background_form.cleaned_data["background"],
        )

        # Get class from class selection step
        klass = class_form.cleaned_data["klass"]

        # Create a mock form for BaseBuilder compatibility
        # BaseBuilder expects ability scores in cleaned_data
        class MockAbilityForm:
            def __init__(self, data):
                self.cleaned_data = data

        ability_data = {
            "strength": ability_form.cleaned_data["strength"],
            "dexterity": ability_form.cleaned_data["dexterity"],
            "constitution": ability_form.cleaned_data["constitution"],
            "intelligence": ability_form.cleaned_data["intelligence"],
            "wisdom": ability_form.cleaned_data["wisdom"],
            "charisma": ability_form.cleaned_data["charisma"],
        }
        mock_form = MockAbilityForm(ability_data)

        # Phase 1: Base setup - inventory and ability scores
        BaseBuilder(character, mock_form).build()

        # Phase 2: Species traits - size, speed, darkvision, languages
        SpeciesBuilder(character).build()

        # Phase 3: Class - HP, proficiencies, features, wealth
        ClassBuilder(character, klass).build()

        # Phase 4: Add skills from skills form
        for field in skills_form.cleaned_data.keys():
            skill_name = skills_form.cleaned_data[field]
            if skill_name:
                character.skills.add(skill_name)

        # Phase 5: Background - skill proficiencies, tools, feat, personality
        BackgroundBuilder(character).build()

        # Phase 6: Derived stats (after all modifiers are applied)
        DerivedStatsBuilder(character).build()

        # Phase 7: Spellcasting setup (if class is a spellcaster)
        SpellcastingBuilder(character, klass).build()

        # Phase 8: Add equipment
        if equipment_form and hasattr(equipment_form, "cleaned_data"):
            inventory = character.inventory
            for field in equipment_form.cleaned_data.keys():
                try:
                    equipment_name = equipment_form.cleaned_data[field]
                    if not equipment_name:
                        continue
                    # If the field is under the form "equipment_name1 & equipment_name2",
                    # each equipment must be added separately.
                    if re.match(MULTI_EQUIPMENT_REGEX, equipment_name):
                        names = equipment_name.split(" & ")
                        for name in names:
                            inventory.add(name)
                    else:
                        inventory.add(equipment_name)
                except KeyError:
                    pass

            # Some equipment is added without selection, depending on character's class.
            match klass.name:
                case ClassName.CLERIC:
                    inventory.add(WeaponName.CROSSBOW_LIGHT)
                    inventory.add(GearName.CROSSBOW_BOLTS)
                    inventory.add(ArmorName.SHIELD)
                case ClassName.ROGUE:
                    inventory.add(WeaponName.SHORTBOW)
                    inventory.add(GearName.QUIVER)
                    inventory.add(ArmorName.LEATHER)
                    inventory.add(WeaponName.DAGGER)
                    inventory.add(WeaponName.DAGGER)
                    inventory.add(ToolName.THIEVES_TOOLS)
                case ClassName.WIZARD:
                    inventory.add(GearName.SPELLBOOK)

        return HttpResponseRedirect(character.get_absolute_url())
