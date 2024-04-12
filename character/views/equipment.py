from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView

from ..forms.equipment import (
    ClericEquipmentSelectForm,
    FighterEquipmentSelectForm,
    RogueEquipmentSelectForm,
    WizardEquipmentSelectForm,
)
from ..constants.equipment import ArmorName, WeaponName, ToolName, GearName
from ..models.klasses import Klass
from .mixins import CharacterContextMixin


class EquipmentSelectView(LoginRequiredMixin, CharacterContextMixin, FormView):
    template_name = "character/equipment_select.html"

    def get_success_url(self):
        return self.character.get_absolute_url()

    def get_form_class(self):
        match self.character.klass:
            case Klass.CLERIC:
                form_class = ClericEquipmentSelectForm
            case Klass.FIGHTER:
                form_class = FighterEquipmentSelectForm
            case Klass.ROGUE:
                form_class = RogueEquipmentSelectForm
            case Klass.WIZARD:
                form_class = WizardEquipmentSelectForm
        return form_class

    def form_valid(self, form):
        inventory = self.character.inventory
        form_fields = [
            "first_weapon",
            "second_weapon",
            "third_weapon",
            "armor",
            "pack",
            "gear",
        ]
        for field in form_fields:
            # KeyError exception is caught because the form is different per class.
            try:
                weapon_name = form.cleaned_data[field]
                inventory.add_equipment(weapon_name)
            except KeyError:
                pass

        # Some equipment is added without selection, depending on character's class.
        match self.character.klass:
            case Klass.CLERIC:
                inventory.add_equipment(WeaponName.CROSSBOW_LIGHT)
                inventory.add_equipment(GearName.CROSSBOW_BOLTS)
                inventory.add_equipment(ArmorName.SHIELD)
            case Klass.ROGUE:
                inventory.add_equipment(WeaponName.SHORTBOW)
                inventory.add_equipment(GearName.QUIVER)
                inventory.add_equipment(ArmorName.LEATHER)
                inventory.add_equipment(WeaponName.DAGGER)
                inventory.add_equipment(WeaponName.DAGGER)
                inventory.add_equipment(ToolName.THIEVES_TOOLS)
            case Klass.WIZARD:
                inventory.add_equipment(GearName.SPELLBOOK)
        return super().form_valid(form)
