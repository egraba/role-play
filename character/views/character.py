import re
from enum import StrEnum

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic import DetailView
from formtools.wizard.views import SessionWizardView

from ..character_attributes_builders import (
    BackgroundBuilder,
    BaseBuilder,
    KlassBuilder,
    RaceBuilder,
)
from ..constants.equipment import ArmorName, GearName, ToolName, WeaponName
from ..forms.backgrounds import BackgroundForm
from ..forms.character import CharacterCreateForm
from ..forms.equipment import EquipmentSelectForm
from ..forms.skills import SkillsSelectForm
from ..models.character import Character
from ..models.klasses import Klass

MULTI_EQUIPMENT_REGEX = r"\S+\s&\s\S+"


class CharacterDetailView(LoginRequiredMixin, DetailView):
    model = Character
    template_name = "character/character.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inventory"] = self.object.inventory
        context["abilities"] = self.object.abilities.all()
        return context


class CharacterCreateView(LoginRequiredMixin, SessionWizardView):
    form_list = [
        CharacterCreateForm,
        SkillsSelectForm,
        BackgroundForm,
        EquipmentSelectForm,
    ]
    template_name = "character/character_create.html"

    class Step(StrEnum):
        BASE_ATTRIBUTES_SELECTION = "0"
        SKILLS_SELECTION = "1"
        BACKGROUND_COMPLETION = "2"
        EQUIPMENT_SELECTION = "3"

    def get_form_initial(self, step):
        if step == self.Step.SKILLS_SELECTION or step == self.Step.EQUIPMENT_SELECTION:
            data = self.storage.get_step_data(self.Step.BASE_ATTRIBUTES_SELECTION)
            if data:
                klass = data.get("0-klass")
                return self.initial_dict.get(step, {"klass": klass})
        if step == self.Step.BACKGROUND_COMPLETION:
            data = self.storage.get_step_data(self.Step.BASE_ATTRIBUTES_SELECTION)
            if data:
                race = data.get("0-race")
                background = data.get("0-background")
                return self.initial_dict.get(
                    step, {"race": race, "background": background}
                )
        return self.initial_dict.get(step, {})

    def done(self, form_list, **kwargs):
        for form in form_list:
            if isinstance(form, CharacterCreateForm):
                character = form.save(commit=False)
                character.user = self.request.user
                BaseBuilder(character, form).build()
                RaceBuilder(character).build()
                KlassBuilder(character).build()
            elif isinstance(form, SkillsSelectForm):
                for field in form.cleaned_data.keys():
                    character.skills.add(form.cleaned_data[field])
            elif isinstance(form, BackgroundForm):
                BackgroundBuilder(character).build()
            elif isinstance(form, EquipmentSelectForm):
                inventory = character.inventory
                for field in form.cleaned_data.keys():
                    # KeyError exception is caught because the form is different per class.
                    try:
                        equipment_name = form.cleaned_data[field]
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
                match character.klass:
                    case Klass.CLERIC:
                        inventory.add(WeaponName.CROSSBOW_LIGHT)
                        inventory.add(GearName.CROSSBOW_BOLTS)
                        inventory.add(ArmorName.SHIELD)
                    case Klass.ROGUE:
                        inventory.add(WeaponName.SHORTBOW)
                        inventory.add(GearName.QUIVER)
                        inventory.add(ArmorName.LEATHER)
                        inventory.add(WeaponName.DAGGER)
                        inventory.add(WeaponName.DAGGER)
                        inventory.add(ToolName.THIEVES_TOOLS)
                    case Klass.WIZARD:
                        inventory.add(GearName.SPELLBOOK)
            else:
                raise NotImplementedError(f"{form=} is not implemented")
        return HttpResponseRedirect(character.get_absolute_url())
