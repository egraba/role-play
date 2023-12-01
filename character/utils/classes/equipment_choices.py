from abc import ABC, abstractmethod

from django.db.models import Q

from character.models.equipment import Armor, Gear, Pack, Weapon


class EquipmentChoicesProvider(ABC):
    """
    Provides methods to get equipment choices per character's class,
    in post creation form.
    """

    @abstractmethod
    def get_weapon1_choices(self):
        pass

    @abstractmethod
    def get_weapon2_choices(self):
        pass

    @abstractmethod
    def get_weapon3_choices(self):
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
