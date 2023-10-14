from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView

from character.forms import ChoseEquipmentForm
from character.models.classes import Class
from character.models.equipment import Armor, Equipment, Gear, Pack, Tool, Weapon
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
                    for pack in Pack.Name.choices
                    if Pack.Name.PRIESTS_PACK in pack
                    or Pack.Name.EXPLORERS_PACK in pack
                ]
                equipment["gear_list"] = [
                    gear
                    for gear in Gear.Name.choices
                    if Gear.Name.AMULET in gear
                    or Gear.Name.EMBLEM in gear
                    or Gear.Name.RELIQUARY in gear
                ]

            case Class.FIGHTER:
                equipment["weapon_list"] = []
                equipment["armor_list"] = []
                equipment["pack_list"] = [
                    pack
                    for pack in Pack.Name.choices
                    if Pack.Name.DUNGEONEERS_PACK in pack
                    or Pack.Name.EXPLORERS_PACK in pack
                ]
                equipment["gear_list"] = []

            case Class.ROGUE:
                equipment["weapon_list"] = [
                    weapon
                    for weapon in Weapon.Name.choices
                    if Weapon.Name.RAPIER in weapon or Weapon.Name.SHORTSWORD in weapon
                ]
                equipment["armor_list"] = []
                equipment["pack_list"] = [
                    pack
                    for pack in Pack.Name.choices
                    if Pack.Name.BURGLARS_PACK in pack
                    or Pack.Name.DUNGEONEERS_PACK in pack
                ]
                equipment["gear_list"] = []

            case Class.WIZARD:
                equipment["weapon_list"] = [
                    weapon
                    for weapon in Weapon.Name.choices
                    if Weapon.Name.QUARTERSTAFF in weapon
                    or Weapon.Name.DAGGER in weapon
                ]
                equipment["armor_list"] = []
                equipment["pack_list"] = [
                    pack
                    for pack in Pack.Name.choices
                    if Pack.Name.SCHOLARS_PACK in pack
                    or Pack.Name.EXPLORERS_PACK in pack
                ]
                equipment["gear_list"] = [
                    gear
                    for gear in Gear.Name.choices
                    if Gear.Name.COMPONENT_POUCH in gear
                    or Gear.Name.CRYSTAL in gear
                    or Gear.Name.ORB in gear
                    or Gear.Name.ROD in gear
                    or Gear.Name.STAFF in gear
                    or Gear.Name.WAND in gear
                ]
        return equipment

    def form_valid(self, form):
        weapon_name = form.cleaned_data["weapon"]
        Equipment.objects.create(name=weapon_name, inventory=self.character.inventory)

        armor_name = form.cleaned_data["armor"]
        Equipment.objects.create(name=armor_name, inventory=self.character.inventory)

        pack_name = form.cleaned_data["pack"]
        Equipment.objects.create(name=pack_name, inventory=self.character.inventory)

        gear_name = form.cleaned_data["gear"]
        Equipment.objects.create(name=gear_name, inventory=self.character.inventory)

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
