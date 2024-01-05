from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView

from character.forms.equipment_selection import EquipmentSelectForm
from character.models.classes import Class
from character.models.equipment import Armor, Equipment, Gear, Tool, Weapon
from character.views.mixins import CharacterContextMixin


class EquipmentSelectView(LoginRequiredMixin, CharacterContextMixin, FormView):
    template_name = "character/equipment_select.html"
    form_class = EquipmentSelectForm

    def get_success_url(self):
        return self.character.get_absolute_url()

    def get_initial(self):
        # The class name is passed to the form, to retrieve appropriate equipment
        # to select.
        initial = dict()
        initial["class_name"] = self.character.class_name
        return initial

    def form_valid(self, form):
        # The form is different per class, so some fields have to be surrunded with try/except.
        weapon_name = form.cleaned_data["weapon1"]
        Equipment.objects.create(name=weapon_name, inventory=self.character.inventory)

        try:
            weapon_name = form.cleaned_data["weapon2"]
            Equipment.objects.create(
                name=weapon_name, inventory=self.character.inventory
            )
        except KeyError:
            pass

        try:
            weapon_name = form.cleaned_data["weapon3"]
            Equipment.objects.create(
                name=weapon_name, inventory=self.character.inventory
            )
        except KeyError:
            pass

        try:
            armor_name = form.cleaned_data["armor"]
            Equipment.objects.create(
                name=armor_name, inventory=self.character.inventory
            )
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
        match self.character.class_name:
            case Class.CLERIC:
                Equipment.objects.create(
                    name=Weapon.Name.CROSSBOW_LIGHT, inventory=self.character.inventory
                )
                Equipment.objects.create(
                    name=Gear.Name.CROSSBOW_BOLTS,
                    inventory=self.character.inventory,
                )
                Equipment.objects.create(
                    name=Armor.Name.SHIELD, inventory=self.character.inventory
                )

            case Class.ROGUE:
                Equipment.objects.create(
                    name=Weapon.Name.SHORTBOW, inventory=self.character.inventory
                )
                Equipment.objects.create(
                    name=Gear.Name.QUIVER, inventory=self.character.inventory
                )
                Equipment.objects.create(
                    name=Armor.Name.LEATHER, inventory=self.character.inventory
                )
                Equipment.objects.create(
                    name=Weapon.Name.DAGGER, inventory=self.character.inventory
                )
                Equipment.objects.create(
                    name=Weapon.Name.DAGGER, inventory=self.character.inventory
                )
                Equipment.objects.create(
                    name=Tool.Name.THIEVES_TOOLS, inventory=self.character.inventory
                )

            case Class.WIZARD:
                Equipment.objects.create(
                    name=Gear.Name.SPELLBOOK,
                    inventory=self.character.inventory,
                )
        return super().form_valid(form)
