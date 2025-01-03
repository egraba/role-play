from abc import ABC, abstractmethod

from django.db.models import Q

from ..constants.equipment import (
    ArmorName,
    GearName,
    GearType,
    WeaponName,
    WeaponType,
    PackName,
)
from ..models.equipment import (
    ArmorSettings,
    GearSettings,
    PackSettings,
    WeaponSettings,
)


class EquipmentChoicesProvider(ABC):
    """
    Provides methods to get equipment choices per character's class,
    in post creation form.
    """

    @abstractmethod
    def get_first_weapon_choices(self):
        pass

    @abstractmethod
    def get_second_weapon_choices(self):
        pass

    @abstractmethod
    def get_third_weapon_choices(self):
        pass

    @abstractmethod
    def get_armor_choices(self):
        pass

    @abstractmethod
    def get_gear_choices(self):
        pass

    @abstractmethod
    def get_pack_choices(self):
        pass


class ClericEquipmentChoicesProvider(EquipmentChoicesProvider):
    def get_first_weapon_choices(self):
        queryset = WeaponSettings.objects.filter(
            Q(name=WeaponName.MACE) | Q(name=WeaponName.WARHAMMER)
        )
        choices = {weapon + weapon for weapon in queryset.values_list("name")}
        return choices

    def get_second_weapon_choices(self):
        queryset = WeaponSettings.objects.filter(
            Q(name=WeaponName.CROSSBOW_LIGHT)
            | Q(weapon_type=WeaponType.SIMPLE_MELEE)
            | Q(weapon_type=WeaponType.SIMPLE_RANGED)
        )
        choices = {weapon + weapon for weapon in queryset.values_list("name")}
        return choices

    def get_third_weapon_choices(self):
        pass

    def get_armor_choices(self):
        queryset = ArmorSettings.objects.filter(
            Q(name=ArmorName.SCALE_MAIL)
            | Q(name=ArmorName.LEATHER)
            | Q(name=ArmorName.CHAIN_MAIL)
        )
        choices = {armor + armor for armor in queryset.values_list("name")}
        return choices

    def get_gear_choices(self):
        queryset = GearSettings.objects.filter(Q(gear_type=GearType.HOLY_SYMBOL))
        choices = {gear + gear for gear in queryset.values_list("name")}
        return choices

    def get_pack_choices(self):
        queryset = PackSettings.objects.filter(
            Q(name=PackName.PRIESTS_PACK) | Q(name=PackName.EXPLORERS_PACK)
        )
        choices = {armor + armor for armor in queryset.values_list("name")}
        return choices


class FighterEquipmentChoicesProvider(EquipmentChoicesProvider):
    def get_first_weapon_choices(self):
        choices = set()
        chain_mail = ArmorSettings.objects.get(name=ArmorName.CHAIN_MAIL).name
        choices.add((chain_mail, chain_mail))
        leather = ArmorSettings.objects.get(name=ArmorName.LEATHER).name
        longbow = WeaponSettings.objects.get(name=WeaponName.LONGBOW).name
        choices.add((f"{leather} & {longbow}", f"{leather} & {longbow}"))
        return choices

    def get_second_weapon_choices(self):
        queryset = WeaponSettings.objects.filter(
            Q(weapon_type=WeaponType.MARTIAL_MELEE)
            | Q(weapon_type=WeaponType.MARTIAL_RANGED)
        )
        choices = {weapon + weapon for weapon in queryset.values_list("name")}
        return choices

    def get_third_weapon_choices(self):
        queryset = WeaponSettings.objects.filter(
            Q(name=WeaponName.CROSSBOW_LIGHT) | Q(name=WeaponName.HANDAXE)
        )
        choices = {weapon + weapon for weapon in queryset.values_list("name")}
        return choices

    def get_armor_choices(self):
        pass

    def get_gear_choices(self):
        pass

    def get_pack_choices(self):
        queryset = PackSettings.objects.filter(
            Q(name=PackName.DUNGEONEERS_PACK) | Q(name=PackName.EXPLORERS_PACK)
        )
        choices = {armor + armor for armor in queryset.values_list("name")}
        return choices


class RogueEquipmentChoicesProvider(EquipmentChoicesProvider):
    def get_first_weapon_choices(self):
        queryset = WeaponSettings.objects.filter(
            Q(name=WeaponName.RAPIER) | Q(name=WeaponName.SHORTSWORD)
        )
        choices = {weapon + weapon for weapon in queryset.values_list("name")}
        return choices

    def get_second_weapon_choices(self):
        queryset = WeaponSettings.objects.filter(
            Q(name=WeaponName.SHORTBOW) | Q(name=WeaponName.SHORTSWORD)
        )
        choices = {weapon + weapon for weapon in queryset.values_list("name")}
        return choices

    def get_third_weapon_choices(self):
        pass

    def get_armor_choices(self):
        pass

    def get_gear_choices(self):
        pass

    def get_pack_choices(self):
        queryset = PackSettings.objects.filter(
            Q(name=PackName.BURGLARS_PACK)
            | Q(name=PackName.DUNGEONEERS_PACK)
            | Q(name=PackName.EXPLORERS_PACK)
        )
        choices = {armor + armor for armor in queryset.values_list("name")}
        return choices


class WizardEquipmentChoicesProvider(EquipmentChoicesProvider):
    def get_first_weapon_choices(self):
        queryset = WeaponSettings.objects.filter(
            Q(name=WeaponName.QUARTERSTAFF) | Q(name=WeaponName.DAGGER)
        )
        choices = {weapon + weapon for weapon in queryset.values_list("name")}
        return choices

    def get_second_weapon_choices(self):
        pass

    def get_third_weapon_choices(self):
        pass

    def get_armor_choices(self):
        pass

    def get_gear_choices(self):
        queryset = GearSettings.objects.filter(
            Q(name=GearName.COMPONENT_POUCH) | Q(gear_type=GearType.ARCANE_FOCUS)
        )
        choices = {gear + gear for gear in queryset.values_list("name")}
        return choices

    def get_pack_choices(self):
        queryset = PackSettings.objects.filter(
            Q(name=PackName.SCHOLARS_PACK) | Q(name=PackName.EXPLORERS_PACK)
        )
        choices = {armor + armor for armor in queryset.values_list("name")}
        return choices
