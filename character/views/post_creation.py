from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView

from character.forms import ChoseEquipmentForm
from character.models.classes import Class
from character.models.equipment import (
    AdventuringGear,
    Armor,
    Equipment,
    EquipmentPack,
    Weapon,
)
from character.views.mixins import CharacterContextMixin


class ChoseEquipmentView(LoginRequiredMixin, CharacterContextMixin, FormView):
    template_name = "character/choose_equipment.html"
    form_class = ChoseEquipmentForm

    def get_success_url(self):
        return self.character.get_absolute_url()

    def get_initial(self):
        # Depending on their class, the character has to select initial weapons.
        # The equipment is passed as dictionary in initial data of the related form.
        equipment = dict()
        match self.character.class_name:
            case Class.CLERIC:
                equipment["weapon_list"] = [
                    weapon
                    for weapon in Weapon.Name.choices
                    if Weapon.Name.MACE in weapon or Weapon.Name.WARHAMMER in weapon
                ]
                equipment["armor_list"] = [
                    armor
                    for armor in Armor.Name.choices
                    if Armor.Name.SCALE_MAIL in armor
                    or Armor.Name.LEATHER in armor
                    or Armor.Name.CHAIN_MAIL in armor
                ]
                equipment["pack_list"] = [
                    pack
                    for pack in EquipmentPack.Name.choices
                    if EquipmentPack.Name.PRIESTS_PACK in pack
                    or EquipmentPack.Name.EXPLORERS_PACK in pack
                ]
                equipment["holy_symbol_list"] = [
                    holy_symbol
                    for holy_symbol in AdventuringGear.Name.choices
                    if AdventuringGear.Name.AMULET in holy_symbol
                    or AdventuringGear.Name.EMBLEM in holy_symbol
                    or AdventuringGear.Name.RELIQUARY in holy_symbol
                ]
            case Class.FIGHTER:
                equipment["weapon_list"] = []
                equipment["armor_list"] = []
            case Class.ROGUE:
                equipment["weapon_list"] = []
                equipment["armor_list"] = []
            case Class.WIZARD:
                equipment["weapon_list"] = []
                equipment["armor_list"] = []
        return equipment

    def form_valid(self, form):
        weapon_name = form.cleaned_data["weapon"]
        Equipment.objects.create(name=weapon_name, inventory=self.character.inventory)
        armor_name = form.cleaned_data["armor"]
        Equipment.objects.create(name=armor_name, inventory=self.character.inventory)
        pack_name = form.cleaned_data["pack"]
        Equipment.objects.create(name=pack_name, inventory=self.character.inventory)
        holy_symbol_name = form.cleaned_data["holy_symbol"]
        Equipment.objects.create(
            name=holy_symbol_name, inventory=self.character.inventory
        )
        # Some equipment is added without selection, depending on character's class.
        match self.character.class_name:
            case Class.CLERIC:
                Equipment.objects.create(
                    name=Armor.Name.SHIELD, inventory=self.character.inventory
                )
        return super().form_valid(form)
