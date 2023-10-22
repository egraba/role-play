from django.db.models import Q

from character.models.classes import Class
from character.models.equipment import Armor, Weapon


def _get_cleric_weapon_choices():
    queryset = Weapon.objects.filter(
        Q(name=Weapon.Name.MACE) | Q(name=Weapon.Name.WARHAMMER)
    )
    choices = {weapon + weapon for weapon in queryset.values_list("name")}
    return choices


def _get_fighter_weapon_choices():
    pass


def _get_rogue_weapon_choices():
    queryset = Weapon.objects.filter(
        Q(name=Weapon.Name.RAPIER) | Q(name=Weapon.Name.SHORTSWORD)
    )
    choices = {weapon + weapon for weapon in queryset.values_list("name")}
    return choices


def _get_wizard_weapon_choices():
    queryset = Weapon.objects.filter(
        Q(name=Weapon.Name.QUARTERSTAFF) | Q(name=Weapon.Name.DAGGER)
    )
    choices = {weapon + weapon for weapon in queryset.values_list("name")}
    return choices


def get_weapon_choices(class_name):
    weapon_choices = []
    match class_name:
        case Class.CLERIC:
            weapon_choices = _get_cleric_weapon_choices()
        case Class.FIGHTER:
            weapon_choices = _get_fighter_weapon_choices()
        case Class.ROGUE:
            weapon_choices = _get_rogue_weapon_choices()
        case Class.WIZARD:
            weapon_choices = _get_wizard_weapon_choices()
    return weapon_choices


def _get_cleric_armor_choices():
    queryset = Armor.objects.filter(
        Q(name=Armor.Name.SCALE_MAIL)
        | Q(name=Armor.Name.LEATHER)
        | Q(name=Armor.Name.CHAIN_MAIL)
    )
    choices = {armor + armor for armor in queryset.values_list("name")}
    return choices


def _get_fighter_armor_choices():
    pass


def _get_rogue_armor_choices():
    pass


def _get_wizard_armor_choices():
    pass


def get_armor_choices(class_name):
    armor_choices = []
    match class_name:
        case Class.CLERIC:
            armor_choices = _get_cleric_armor_choices()
        case Class.FIGHTER:
            armor_choices = _get_fighter_armor_choices()
        case Class.ROGUE:
            armor_choices = _get_rogue_armor_choices()
        case Class.WIZARD:
            armor_choices = _get_wizard_armor_choices()
    return armor_choices
