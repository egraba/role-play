import pytest

from equipment.constants.equipment import ArmorName, GearName, PackName, WeaponName
from character.forms.equipment_choices_providers import (
    ClericEquipmentChoicesProvider,
    FighterEquipmentChoicesProvider,
    RogueEquipmentChoicesProvider,
    WizardEquipmentChoicesProvider,
)
from utils.converters import duplicate_choice

pytestmark = pytest.mark.django_db


class TestClericEquipmentChoicesProvider:
    def test_get_first_weapon_choices(self):
        choices_provider = ClericEquipmentChoicesProvider()
        choices = choices_provider.get_first_weapon_choices()
        assert choices == {
            duplicate_choice(WeaponName.MACE),
            duplicate_choice(WeaponName.WARHAMMER),
        }

    def test_get_second_weapon_choices(self):
        choices_provider = ClericEquipmentChoicesProvider()
        choices = choices_provider.get_second_weapon_choices()
        assert choices == {
            duplicate_choice(WeaponName.CROSSBOW_LIGHT),
            duplicate_choice(WeaponName.CLUB),
            duplicate_choice(WeaponName.DAGGER),
            duplicate_choice(WeaponName.GREATCLUB),
            duplicate_choice(WeaponName.HANDAXE),
            duplicate_choice(WeaponName.JAVELIN),
            duplicate_choice(WeaponName.LIGHT_HAMMER),
            duplicate_choice(WeaponName.MACE),
            duplicate_choice(WeaponName.QUARTERSTAFF),
            duplicate_choice(WeaponName.SICKLE),
            duplicate_choice(WeaponName.SPEAR),
            duplicate_choice(WeaponName.DART),
            duplicate_choice(WeaponName.SHORTBOW),
            duplicate_choice(WeaponName.SLING),
        }

    def test_get_third_weapon_choices(self):
        choices_provider = ClericEquipmentChoicesProvider()
        assert choices_provider.get_third_weapon_choices() is None

    def test_get_armor_choices(self):
        choices_provider = ClericEquipmentChoicesProvider()
        choices = choices_provider.get_armor_choices()
        assert choices == {
            duplicate_choice(ArmorName.SCALE_MAIL),
            duplicate_choice(ArmorName.LEATHER),
            duplicate_choice(ArmorName.CHAIN_MAIL),
        }

    def test_get_gear_choices(self):
        choices_provider = ClericEquipmentChoicesProvider()
        choices = choices_provider.get_gear_choices()
        assert choices == {
            duplicate_choice(GearName.AMULET),
            duplicate_choice(GearName.EMBLEM),
            duplicate_choice(GearName.RELIQUARY),
        }

    def test_get_pack_choices(self):
        choices_provider = ClericEquipmentChoicesProvider()
        choices = choices_provider.get_pack_choices()
        assert choices == {
            duplicate_choice(PackName.PRIESTS_PACK),
            duplicate_choice(PackName.EXPLORERS_PACK),
        }


class TestFighterEquipmentChoicesProvider:
    def test_get_first_weapon_choices(self):
        choices_provider = FighterEquipmentChoicesProvider()
        choices = choices_provider.get_first_weapon_choices()
        assert choices == {
            duplicate_choice(ArmorName.CHAIN_MAIL),
            duplicate_choice(ArmorName.LEATHER, WeaponName.LONGBOW),
        }

    def test_get_second_weapon_choices(self):
        choices_provider = FighterEquipmentChoicesProvider()
        choices = choices_provider.get_second_weapon_choices()
        assert choices == {
            duplicate_choice(WeaponName.BATTLEAXE),
            duplicate_choice(WeaponName.FLAIL),
            duplicate_choice(WeaponName.GLAIVE),
            duplicate_choice(WeaponName.GREATAXE),
            duplicate_choice(WeaponName.GREATSWORD),
            duplicate_choice(WeaponName.HALBERD),
            duplicate_choice(WeaponName.LANCE),
            duplicate_choice(WeaponName.LONGSWORD),
            duplicate_choice(WeaponName.MAUL),
            duplicate_choice(WeaponName.MORNINGSTAR),
            duplicate_choice(WeaponName.PIKE),
            duplicate_choice(WeaponName.RAPIER),
            duplicate_choice(WeaponName.SCIMITAR),
            duplicate_choice(WeaponName.SHORTSWORD),
            duplicate_choice(WeaponName.TRIDENT),
            duplicate_choice(WeaponName.WAR_PICK),
            duplicate_choice(WeaponName.WARHAMMER),
            duplicate_choice(WeaponName.WHIP),
            duplicate_choice(WeaponName.BLOWGUN),
            duplicate_choice(WeaponName.CROSSBOW_HAND),
            duplicate_choice(WeaponName.CROSSBOW_HEAVY),
            duplicate_choice(WeaponName.LONGBOW),
            duplicate_choice(WeaponName.NET),
        }

    def test_get_third_weapon_choices(self):
        choices_provider = FighterEquipmentChoicesProvider()
        choices = choices_provider.get_third_weapon_choices()
        assert choices == {
            duplicate_choice(WeaponName.CROSSBOW_LIGHT),
            duplicate_choice(WeaponName.HANDAXE),
        }

    def test_get_armor_choices(self):
        choices_provider = FighterEquipmentChoicesProvider()
        assert choices_provider.get_armor_choices() is None

    def test_get_gear_choices(self):
        choices_provider = FighterEquipmentChoicesProvider()
        assert choices_provider.get_gear_choices() is None

    def test_get_pack_choices(self):
        choices_provider = FighterEquipmentChoicesProvider()
        choices = choices_provider.get_pack_choices()
        assert choices == {
            duplicate_choice(PackName.DUNGEONEERS_PACK),
            duplicate_choice(PackName.EXPLORERS_PACK),
        }


class TestRogueEquipmentChoicesProvider:
    def test_get_first_weapon_choices(self):
        choices_provider = RogueEquipmentChoicesProvider()
        choices = choices_provider.get_first_weapon_choices()
        assert choices == {
            duplicate_choice(WeaponName.RAPIER),
            duplicate_choice(WeaponName.SHORTSWORD),
        }

    def test_get_second_weapon_choices(self):
        choices_provider = RogueEquipmentChoicesProvider()
        choices = choices_provider.get_second_weapon_choices()
        assert choices == {
            duplicate_choice(WeaponName.SHORTBOW),
            duplicate_choice(WeaponName.SHORTSWORD),
        }

    def test_get_third_weapon_choices(self):
        choices_provider = RogueEquipmentChoicesProvider()
        assert choices_provider.get_third_weapon_choices() is None

    def test_get_armor_choices(self):
        choices_provider = RogueEquipmentChoicesProvider()
        assert choices_provider.get_armor_choices() is None

    def test_get_gear_choices(self):
        choices_provider = RogueEquipmentChoicesProvider()
        assert choices_provider.get_gear_choices() is None

    def test_get_pack_choices(self):
        choices_provider = RogueEquipmentChoicesProvider()
        choices = choices_provider.get_pack_choices()
        assert choices == {
            duplicate_choice(PackName.BURGLARS_PACK),
            duplicate_choice(PackName.DUNGEONEERS_PACK),
            duplicate_choice(PackName.EXPLORERS_PACK),
        }


class TestWizardEquipmentChoicesProvider:
    def test_get_first_weapon_choices(self):
        choices_provider = WizardEquipmentChoicesProvider()
        choices = choices_provider.get_first_weapon_choices()
        assert choices == {
            duplicate_choice(WeaponName.QUARTERSTAFF),
            duplicate_choice(WeaponName.DAGGER),
        }

    def test_get_second_weapon_choices(self):
        choices_provider = WizardEquipmentChoicesProvider()
        assert choices_provider.get_second_weapon_choices() is None

    def test_get_third_weapon_choices(self):
        choices_provider = WizardEquipmentChoicesProvider()
        assert choices_provider.get_third_weapon_choices() is None

    def test_get_armor_choices(self):
        choices_provider = WizardEquipmentChoicesProvider()
        assert choices_provider.get_armor_choices() is None

    def test_get_gear_choices(self):
        choices_provider = WizardEquipmentChoicesProvider()
        choices = choices_provider.get_gear_choices()
        assert choices == {
            duplicate_choice(GearName.COMPONENT_POUCH),
            duplicate_choice(GearName.CRYSTAL),
            duplicate_choice(GearName.ORB),
            duplicate_choice(GearName.ROD),
            duplicate_choice(GearName.STAFF),
            duplicate_choice(GearName.WAND),
        }

    def test_get_pack_choices(self):
        choices_provider = WizardEquipmentChoicesProvider()
        choices = choices_provider.get_pack_choices()
        assert choices == {
            duplicate_choice(PackName.SCHOLARS_PACK),
            duplicate_choice(PackName.EXPLORERS_PACK),
        }
