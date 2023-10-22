from django.db.models import Q

from character.models.classes import Class
from character.models.equipment import Weapon


def _get_cleric_weapon_choices():
    queryset = Weapon.objects.filter(
        Q(name=Weapon.Name.MACE) | Q(name=Weapon.Name.WARHAMMER)
    )
    choices = [weapon + weapon for weapon in queryset.values_list("name")]
    return choices


def get_weapon_choices(class_name):
    weapon_choices = []
    match class_name:
        case Class.CLERIC:
            weapon_choices = _get_cleric_weapon_choices()
        case Class.FIGHTER:
            pass
        case Class.ROGUE:
            pass
        case Class.WIZARD:
            pass
    return weapon_choices
