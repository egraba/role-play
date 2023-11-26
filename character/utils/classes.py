from django.db.models import Q

from character.models.classes import Class
from character.models.equipment import Armor, Gear, Pack, Weapon


def _get_cleric_weapon1_choices():
    queryset = Weapon.objects.filter(
        Q(name=Weapon.Name.MACE) | Q(name=Weapon.Name.WARHAMMER)
    )
    choices = {weapon + weapon for weapon in queryset.values_list("name")}
    return choices


def _get_fighter_weapon1_choices():
    choices = set()
    chain_mail = Armor.objects.get(name=Armor.Name.CHAIN_MAIL).name
    choices.add((chain_mail, chain_mail))
    leather = Armor.objects.get(name=Armor.Name.LEATHER).name
    longbow = Weapon.objects.get(name=Weapon.Name.LONGBOW).name
    choices.add((f"{leather} & {longbow}", f"{leather} & {longbow}"))
    return choices


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
    weapon_choices = set()
    match class_name:
        case Class.CLERIC:
            weapon_choices = _get_cleric_weapon1_choices()
        case Class.FIGHTER:
            weapon_choices = _get_fighter_weapon1_choices()
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


def _get_fighter_weapon2_choices():
    queryset = Weapon.objects.filter(
        Q(weapon_type=Weapon.Type.MARTIAL_MELEE)
        | Q(weapon_type=Weapon.Type.MARTIAL_RANGED)
    )
    choices = {weapon + weapon for weapon in queryset.values_list("name")}
    return choices


def _get_rogue_weapon2_choices():
    queryset = Weapon.objects.filter(
        Q(name=Weapon.Name.SHORTBOW) | Q(name=Weapon.Name.SHORTSWORD)
    )
    choices = {weapon + weapon for weapon in queryset.values_list("name")}
    return choices


def get_weapon2_choices(class_name):
    weapon_choices = []
    match class_name:
        case Class.CLERIC:
            weapon_choices = _get_cleric_weapon2_choices()
        case Class.FIGHTER:
            weapon_choices = _get_fighter_weapon2_choices()
        case Class.ROGUE:
            weapon_choices = _get_rogue_weapon2_choices()
        case Class.WIZARD:
            weapon_choices = _get_wizard_weapon_choices()
    return weapon_choices


def _get_fighter_weapon3_choices():
    queryset = Weapon.objects.filter(
        Q(name=Weapon.Name.CROSSBOW_LIGHT) | Q(name=Weapon.Name.HANDAXE)
    )
    choices = {weapon + weapon for weapon in queryset.values_list("name")}
    return choices


def get_weapon3_choices(class_name):
    weapon_choices = []
    match class_name:
        case Class.FIGHTER:
            weapon_choices = _get_fighter_weapon3_choices()
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


def _get_cleric_gear_choices():
    queryset = Gear.objects.filter(Q(gear_type=Gear.Type.HOLY_SYMBOL))
    choices = {gear + gear for gear in queryset.values_list("name")}
    return choices


def _get_wizard_gear_choices():
    queryset = Gear.objects.filter(
        Q(name=Gear.Name.COMPONENT_POUCH) | Q(gear_type=Gear.Type.ARCANE_FOCUS)
    )
    choices = {gear + gear for gear in queryset.values_list("name")}
    return choices


def get_gear_choices(class_name):
    gear_choices = []
    match class_name:
        case Class.CLERIC:
            gear_choices = _get_cleric_gear_choices()
        case Class.WIZARD:
            gear_choices = _get_wizard_gear_choices()
    return gear_choices
