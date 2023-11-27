from django.db.models import Q

from character.models.equipment import Pack, Weapon

from .choices import EquipmentChoicesProvider


class RogueEquipmentChoicesProvider(EquipmentChoicesProvider):
    def get_weapon1_choices(self):
        queryset = Weapon.objects.filter(
            Q(name=Weapon.Name.RAPIER) | Q(name=Weapon.Name.SHORTSWORD)
        )
        choices = {weapon + weapon for weapon in queryset.values_list("name")}
        return choices

    def get_weapon2_choices(self):
        queryset = Weapon.objects.filter(
            Q(name=Weapon.Name.SHORTBOW) | Q(name=Weapon.Name.SHORTSWORD)
        )
        choices = {weapon + weapon for weapon in queryset.values_list("name")}
        return choices

    def get_weapon3_choices(self):
        raise NotImplementedError

    def get_armor_choices(self):
        raise NotImplementedError

    def get_gear_choices(self):
        raise NotImplementedError

    def get_pack_choices(self):
        queryset = Pack.objects.filter(
            Q(name=Pack.Name.BURGLARS_PACK)
            | Q(name=Pack.Name.DUNGEONEERS_PACK)
            | Q(name=Pack.Name.EXPLORERS_PACK)
        )
        choices = {armor + armor for armor in queryset.values_list("name")}
        return choices
