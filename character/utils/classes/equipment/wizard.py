from django.db.models import Q

from character.models.equipment import Gear, Pack, Weapon

from .choices import EquipmentChoicesProvider


class WizardEquipmentChoicesProvider(EquipmentChoicesProvider):
    def get_weapon1_choices(self):
        queryset = Weapon.objects.filter(
            Q(name=Weapon.Name.QUARTERSTAFF) | Q(name=Weapon.Name.DAGGER)
        )
        choices = {weapon + weapon for weapon in queryset.values_list("name")}
        return choices

    def get_weapon2_choices(self):
        raise NotImplementedError

    def get_weapon3_choices(self):
        raise NotImplementedError

    def get_armor_choices(self):
        raise NotImplementedError

    def get_gear_choices(self):
        queryset = Gear.objects.filter(
            Q(name=Gear.Name.COMPONENT_POUCH) | Q(gear_type=Gear.Type.ARCANE_FOCUS)
        )
        choices = {gear + gear for gear in queryset.values_list("name")}
        return choices

    def get_pack_choices(self):
        queryset = Pack.objects.filter(
            Q(name=Pack.Name.SCHOLARS_PACK) | Q(name=Pack.Name.EXPLORERS_PACK)
        )
        choices = {armor + armor for armor in queryset.values_list("name")}
        return choices
