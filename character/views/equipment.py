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
from ..models.equipment import Equipment
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
        # The form is different per class, so some fields have to be surrunded with try/except.
        weapon_name = form.cleaned_data["first_weapon"]
        Equipment.objects.create(name=weapon_name, inventory=self.character.inventory)

        try:
            weapon_name = form.cleaned_data["second_weapon"]
            Equipment.objects.create(
                name=weapon_name, inventory=self.character.inventory
            )
        except KeyError:
            pass

        try:
            weapon_name = form.cleaned_data["third_weapon"]
            Equipment.objects.create(
                name=weapon_name, inventory=self.character.inventory
            )
        except KeyError:
            pass

        try:
            name = form.cleaned_data["armor"]
            Equipment.objects.create(name=name, inventory=self.character.inventory)
        except KeyError:
            pass

        pack_name = form.cleaned_data["pack"]
        Equipment.objects.create(name=pack_name, inventory=self.character.inventory)

        try:
            gear_name = form.cleaned_data["gear"]
            Equipment.objects.create(name=gear_name, inventory=self.character.inventory)
        except KeyError:
            pass

        # Some equipment is added without selection, depending on character's class.
        match self.character.klass:
            case Klass.CLERIC:
                Equipment.objects.create(
                    name=WeaponName.CROSSBOW_LIGHT, inventory=self.character.inventory
                )
                Equipment.objects.create(
                    name=GearName.CROSSBOW_BOLTS,
                    inventory=self.character.inventory,
                )
                Equipment.objects.create(
                    name=ArmorName.SHIELD, inventory=self.character.inventory
                )

            case Klass.ROGUE:
                Equipment.objects.create(
                    name=WeaponName.SHORTBOW, inventory=self.character.inventory
                )
                Equipment.objects.create(
                    name=GearName.QUIVER, inventory=self.character.inventory
                )
                Equipment.objects.create(
                    name=ArmorName.LEATHER, inventory=self.character.inventory
                )
                Equipment.objects.create(
                    name=WeaponName.DAGGER, inventory=self.character.inventory
                )
                Equipment.objects.create(
                    name=WeaponName.DAGGER, inventory=self.character.inventory
                )
                Equipment.objects.create(
                    name=ToolName.THIEVES_TOOLS, inventory=self.character.inventory
                )

            case Klass.WIZARD:
                Equipment.objects.create(
                    name=GearName.SPELLBOOK,
                    inventory=self.character.inventory,
                )
        return super().form_valid(form)
