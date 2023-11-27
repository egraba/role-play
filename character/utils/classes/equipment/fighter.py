from django.db.models import Q

from character.models.equipment import Armor, Pack, Weapon

from .choices import EquipmentChoicesProvider


class FighterEquipmentChoicesProvider(EquipmentChoicesProvider):
    def get_weapon1_choices(self):
        choices = set()
        chain_mail = Armor.objects.get(name=Armor.Name.CHAIN_MAIL).name
        choices.add((chain_mail, chain_mail))
        leather = Armor.objects.get(name=Armor.Name.LEATHER).name
        longbow = Weapon.objects.get(name=Weapon.Name.LONGBOW).name
        choices.add((f"{leather} & {longbow}", f"{leather} & {longbow}"))
        return choices

    def get_weapon2_choices(self):
        queryset = Weapon.objects.filter(
            Q(weapon_type=Weapon.Type.MARTIAL_MELEE)
            | Q(weapon_type=Weapon.Type.MARTIAL_RANGED)
        )
        choices = {weapon + weapon for weapon in queryset.values_list("name")}
        return choices

    def get_weapon3_choices(self):
        queryset = Weapon.objects.filter(
            Q(name=Weapon.Name.CROSSBOW_LIGHT) | Q(name=Weapon.Name.HANDAXE)
        )
        choices = {weapon + weapon for weapon in queryset.values_list("name")}
        return choices

    def get_armor_choices(self):
        raise NotImplementedError

    def get_gear_choices(self):
        raise NotImplementedError

    def get_pack_choices(self):
        queryset = Pack.objects.filter(
            Q(name=Pack.Name.DUNGEONEERS_PACK) | Q(name=Pack.Name.EXPLORERS_PACK)
        )
        choices = {armor + armor for armor in queryset.values_list("name")}
        return choices
