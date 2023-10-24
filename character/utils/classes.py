from django.db.models import Q

from character.models.classes import Class
from character.models.equipment import Armor, Pack, Weapon


def _get_cleric_weapon1_choices():
    queryset = Weapon.objects.filter(
        Q(name=Weapon.Name.MACE) | Q(name=Weapon.Name.WARHAMMER)
    )
    choices = {weapon + weapon for weapon in queryset.values_list("name")}
    return choices


def _get_fighter_weapon_choices():
    return {}


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


def get_weapon1_choices(class_name):
    weapon_choices = []
    match class_name:
        case Class.CLERIC:
            weapon_choices = _get_cleric_weapon1_choices()
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


def _get_cleric_weapon2_choices():
    queryset = Weapon.objects.filter(
        Q(name=Weapon.Name.CROSSBOW_LIGHT)
        | Q(weapon_type=Weapon.Type.SIMPLE_MELEE)
        | Q(weapon_type=Weapon.Type.SIMPLE_RANGED)
    )
    choices = {weapon + weapon for weapon in queryset.values_list("name")}
    return choices


def get_weapon2_choices(class_name):
    weapon_choices = []
    match class_name:
        case Class.CLERIC:
            weapon_choices = _get_cleric_weapon2_choices()
        case Class.FIGHTER:
            weapon_choices = _get_fighter_weapon_choices()
        case Class.ROGUE:
            weapon_choices = _get_rogue_weapon_choices()
        case Class.WIZARD:
            weapon_choices = _get_wizard_weapon_choices()
    return weapon_choices


def _get_cleric_pack_choices():
    queryset = Pack.objects.filter(
        Q(name=Pack.Name.PRIESTS_PACK) | Q(name=Pack.Name.EXPLORERS_PACK)
    )
    choices = {armor + armor for armor in queryset.values_list("name")}
    return choices


def _get_fighter_pack_choices():
    queryset = Pack.objects.filter(
        Q(name=Pack.Name.DUNGEONEERS_PACK) | Q(name=Pack.Name.EXPLORERS_PACK)
    )
    choices = {armor + armor for armor in queryset.values_list("name")}
    return choices


def _get_rogue_pack_choices():
    queryset = Pack.objects.filter(
        Q(name=Pack.Name.BURGLARS_PACK)
        | Q(name=Pack.Name.DUNGEONEERS_PACK)
        | Q(name=Pack.Name.EXPLORERS_PACK)
    )
    choices = {armor + armor for armor in queryset.values_list("name")}
    return choices


def _get_wizard_pack_choices():
    queryset = Pack.objects.filter(
        Q(name=Pack.Name.SCHOLARS_PACK) | Q(name=Pack.Name.EXPLORERS_PACK)
    )
    choices = {armor + armor for armor in queryset.values_list("name")}
    return choices


def get_pack_choices(class_name):
    pack_choices = []
    match class_name:
        case Class.CLERIC:
            pack_choices = _get_cleric_pack_choices()
        case Class.FIGHTER:
            pack_choices = _get_fighter_pack_choices()
        case Class.ROGUE:
            pack_choices = _get_rogue_pack_choices()
        case Class.WIZARD:
            pack_choices = _get_wizard_pack_choices()
    return pack_choices


def get_gear_choices(class_name):
    gear_choices = []
    match class_name:
        case Class.WIZARD:
            gear_choices = {}
    return gear_choices
