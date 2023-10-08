from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView

from character.forms import ChoseEquipmentForm
from character.models.classes import Class
from character.models.equipment import Armor, EquipmentPack, Weapon
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
        Weapon.objects.create(name=weapon_name, inventory=self.character.inventory)
        armor_name = form.cleaned_data["armor"]
        Armor.objects.create(name=armor_name, inventory=self.character.inventory)
        return super().form_valid(form)
