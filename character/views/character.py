import json
from enum import StrEnum

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic import DetailView
from formtools.wizard.views import SessionWizardView

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
from ..services import CharacterCreationService, CharacterSheetService


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

        species_form = forms_by_type.get("SpeciesSelectForm")
        class_form = forms_by_type.get("ClassSelectForm")
        ability_form = forms_by_type.get("AbilityScoreForm")
        background_form = forms_by_type.get("BackgroundSelectForm")
        skills_form = forms_by_type.get("SkillsSelectForm")
        equipment_form = forms_by_type.get("EquipmentSelectForm")
        review_form = forms_by_type.get("ReviewForm")

        klass = class_form.cleaned_data["klass"]

        # Collect skills
        skills = [
            skills_form.cleaned_data[field]
            for field in skills_form.cleaned_data
            if skills_form.cleaned_data[field]
        ]

        # Collect equipment
        equipment = []
        if equipment_form and hasattr(equipment_form, "cleaned_data"):
            equipment = [
                equipment_form.cleaned_data[field]
                for field in equipment_form.cleaned_data
                if equipment_form.cleaned_data.get(field)
            ]

        character = CharacterCreationService.create_character(
            user=self.request.user,
            name=review_form.cleaned_data["name"],
            species=species_form.cleaned_data["species"],
            klass=klass,
            abilities={
                "strength": ability_form.cleaned_data["strength"],
                "dexterity": ability_form.cleaned_data["dexterity"],
                "constitution": ability_form.cleaned_data["constitution"],
                "intelligence": ability_form.cleaned_data["intelligence"],
                "wisdom": ability_form.cleaned_data["wisdom"],
                "charisma": ability_form.cleaned_data["charisma"],
            },
            background=background_form.cleaned_data["background"],
            skills=skills,
            equipment=equipment,
        )

        return HttpResponseRedirect(character.get_absolute_url())
