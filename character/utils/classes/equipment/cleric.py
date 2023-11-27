from django.db.models import Q

from character.models.equipment import Armor, Gear, Pack, Weapon

from .choices import EquipmentChoicesProvider


class ClericEquipmentChoicesProvider(EquipmentChoicesProvider):
    def get_weapon1_choices(self):
        queryset = Weapon.objects.filter(
            Q(name=Weapon.Name.MACE) | Q(name=Weapon.Name.WARHAMMER)
        )
        choices = {weapon + weapon for weapon in queryset.values_list("name")}
        return choices

    def get_weapon2_choices(self):
        queryset = Weapon.objects.filter(
            Q(name=Weapon.Name.CROSSBOW_LIGHT)
            | Q(weapon_type=Weapon.Type.SIMPLE_MELEE)
            | Q(weapon_type=Weapon.Type.SIMPLE_RANGED)
        )
        choices = {weapon + weapon for weapon in queryset.values_list("name")}
        return choices

    def get_weapon3_choices(self):
        raise NotImplementedError

    def get_armor_choices(self):
        queryset = Armor.objects.filter(
            Q(name=Armor.Name.SCALE_MAIL)
            | Q(name=Armor.Name.LEATHER)
            | Q(name=Armor.Name.CHAIN_MAIL)
        )
        choices = {armor + armor for armor in queryset.values_list("name")}
        return choices

    def get_gear_choices(self):
        queryset = Gear.objects.filter(Q(gear_type=Gear.Type.HOLY_SYMBOL))
        choices = {gear + gear for gear in queryset.values_list("name")}
        return choices

    def get_pack_choices(self):
        queryset = Pack.objects.filter(
            Q(name=Pack.Name.PRIESTS_PACK) | Q(name=Pack.Name.EXPLORERS_PACK)
        )
        choices = {armor + armor for armor in queryset.values_list("name")}
        return choices
