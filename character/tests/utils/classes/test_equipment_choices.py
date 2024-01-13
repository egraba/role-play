import pytest

from character.models.equipment import Armor, Gear, Pack, Weapon
from character.utils.equipment import (
    ClericEquipmentChoicesProvider,
    FighterEquipmentChoicesProvider,
    RogueEquipmentChoicesProvider,
    WizardEquipmentChoicesProvider,
)
from utils.converters import duplicate_choice


@pytest.mark.django_db
class TestClericEquipmentChoicesProvider:
    def test_get_first_weapon_choices(self):
        equipment_provider = ClericEquipmentChoicesProvider()
        choices = equipment_provider.get_first_weapon_choices()
        assert choices == {
            duplicate_choice(Weapon.Name.MACE),
            duplicate_choice(Weapon.Name.WARHAMMER),
        }

    def test_get_second_weapon_choices(self):
        equipment_provider = ClericEquipmentChoicesProvider()
        choices = equipment_provider.get_second_weapon_choices()
        assert choices == {
            duplicate_choice(Weapon.Name.CROSSBOW_LIGHT),
            duplicate_choice(Weapon.Name.CLUB),
            duplicate_choice(Weapon.Name.DAGGER),
            duplicate_choice(Weapon.Name.GREATCLUB),
            duplicate_choice(Weapon.Name.HANDAXE),
            duplicate_choice(Weapon.Name.JAVELIN),
            duplicate_choice(Weapon.Name.LIGHT_HAMMER),
            duplicate_choice(Weapon.Name.MACE),
            duplicate_choice(Weapon.Name.QUARTERSTAFF),
            duplicate_choice(Weapon.Name.SICKLE),
            duplicate_choice(Weapon.Name.SPEAR),
            duplicate_choice(Weapon.Name.DART),
            duplicate_choice(Weapon.Name.SHORTBOW),
            duplicate_choice(Weapon.Name.SLING),
        }

    def test_get_third_weapon_choices(self):
        equipment_provider = ClericEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_third_weapon_choices()

    def test_get_armor_choices(self):
        equipment_provider = ClericEquipmentChoicesProvider()
        choices = equipment_provider.get_armor_choices()
        assert choices == {
            duplicate_choice(Armor.Name.SCALE_MAIL),
            duplicate_choice(Armor.Name.LEATHER),
            duplicate_choice(Armor.Name.CHAIN_MAIL),
        }

    def test_get_gear_choices(self):
        equipment_provider = ClericEquipmentChoicesProvider()
        choices = equipment_provider.get_gear_choices()
        assert choices == {
            duplicate_choice(Gear.Name.AMULET),
            duplicate_choice(Gear.Name.EMBLEM),
            duplicate_choice(Gear.Name.RELIQUARY),
        }

    def test_get_pack_choices(self):
        equipment_provider = ClericEquipmentChoicesProvider()
        choices = equipment_provider.get_pack_choices()
        assert choices == {
            duplicate_choice(Pack.Name.PRIESTS_PACK),
            duplicate_choice(Pack.Name.EXPLORERS_PACK),
        }


@pytest.mark.django_db
class TestFighterEquipmentChoicesProvider:
    def test_get_first_weapon_choices(self):
        equipment_provider = FighterEquipmentChoicesProvider()
        choices = equipment_provider.get_first_weapon_choices()
        assert choices == {
            duplicate_choice(Armor.Name.CHAIN_MAIL),
            duplicate_choice(Armor.Name.LEATHER, Weapon.Name.LONGBOW),
        }

    def test_get_second_weapon_choices(self):
        equipment_provider = FighterEquipmentChoicesProvider()
        choices = equipment_provider.get_second_weapon_choices()
        assert choices == {
            duplicate_choice(Weapon.Name.BATTLEAXE),
            duplicate_choice(Weapon.Name.FLAIL),
            duplicate_choice(Weapon.Name.GLAIVE),
            duplicate_choice(Weapon.Name.GREATAXE),
            duplicate_choice(Weapon.Name.GREATSWORD),
            duplicate_choice(Weapon.Name.HALBERD),
            duplicate_choice(Weapon.Name.LANCE),
            duplicate_choice(Weapon.Name.LONGSWORD),
            duplicate_choice(Weapon.Name.MAUL),
            duplicate_choice(Weapon.Name.MORNINGSTAR),
            duplicate_choice(Weapon.Name.PIKE),
            duplicate_choice(Weapon.Name.RAPIER),
            duplicate_choice(Weapon.Name.SCIMITAR),
            duplicate_choice(Weapon.Name.SHORTSWORD),
            duplicate_choice(Weapon.Name.TRIDENT),
            duplicate_choice(Weapon.Name.WAR_PICK),
            duplicate_choice(Weapon.Name.WARHAMMER),
            duplicate_choice(Weapon.Name.WHIP),
            duplicate_choice(Weapon.Name.BLOWGUN),
            duplicate_choice(Weapon.Name.CROSSBOW_HAND),
            duplicate_choice(Weapon.Name.CROSSBOW_HEAVY),
            duplicate_choice(Weapon.Name.LONGBOW),
            duplicate_choice(Weapon.Name.NET),
        }

    def test_get_third_weapon_choices(self):
        equipment_provider = FighterEquipmentChoicesProvider()
        choices = equipment_provider.get_third_weapon_choices()
        assert choices == {
            duplicate_choice(Weapon.Name.CROSSBOW_LIGHT),
            duplicate_choice(Weapon.Name.HANDAXE),
        }

    def test_get_armor_choices(self):
        equipment_provider = FighterEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_armor_choices()

    def test_get_gear_choices(self):
        equipment_provider = FighterEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_gear_choices()

    def test_get_pack_choices(self):
        equipment_provider = FighterEquipmentChoicesProvider()
        choices = equipment_provider.get_pack_choices()
        assert choices == {
            duplicate_choice(Pack.Name.DUNGEONEERS_PACK),
            duplicate_choice(Pack.Name.EXPLORERS_PACK),
        }


@pytest.mark.django_db
class TestRogueEquipmentChoicesProvider:
    def test_get_first_weapon_choices(self):
        equipment_provider = RogueEquipmentChoicesProvider()
        choices = equipment_provider.get_first_weapon_choices()
        assert choices == {
            duplicate_choice(Weapon.Name.RAPIER),
            duplicate_choice(Weapon.Name.SHORTSWORD),
        }

    def test_get_second_weapon_choices(self):
        equipment_provider = RogueEquipmentChoicesProvider()
        choices = equipment_provider.get_second_weapon_choices()
        assert choices == {
            duplicate_choice(Weapon.Name.SHORTBOW),
            duplicate_choice(Weapon.Name.SHORTSWORD),
        }

    def test_get_third_weapon_choices(self):
        equipment_provider = RogueEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_third_weapon_choices()

    def test_get_armor_choices(self):
        equipment_provider = RogueEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_armor_choices()

    def test_get_gear_choices(self):
        equipment_provider = RogueEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_gear_choices()

    def test_get_pack_choices(self):
        equipment_provider = RogueEquipmentChoicesProvider()
        choices = equipment_provider.get_pack_choices()
        assert choices == {
            duplicate_choice(Pack.Name.BURGLARS_PACK),
            duplicate_choice(Pack.Name.DUNGEONEERS_PACK),
            duplicate_choice(Pack.Name.EXPLORERS_PACK),
        }


@pytest.mark.django_db
class TestWizardEquipmentChoicesProvider:
    def test_get_first_weapon_choices(self):
        equipment_provider = WizardEquipmentChoicesProvider()
        choices = equipment_provider.get_first_weapon_choices()
        assert choices == {
            duplicate_choice(Weapon.Name.QUARTERSTAFF),
            duplicate_choice(Weapon.Name.DAGGER),
        }

    def test_get_second_weapon_choices(self):
        equipment_provider = WizardEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_second_weapon_choices()

    def test_get_third_weapon_choices(self):
        equipment_provider = WizardEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_third_weapon_choices()

    def test_get_armor_choices(self):
        equipment_provider = WizardEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_armor_choices()

    def test_get_gear_choices(self):
        equipment_provider = WizardEquipmentChoicesProvider()
        choices = equipment_provider.get_gear_choices()
        assert choices == {
            duplicate_choice(Gear.Name.COMPONENT_POUCH),
            duplicate_choice(Gear.Name.CRYSTAL),
            duplicate_choice(Gear.Name.ORB),
            duplicate_choice(Gear.Name.ROD),
            duplicate_choice(Gear.Name.STAFF),
            duplicate_choice(Gear.Name.WAND),
        }

    def test_get_pack_choices(self):
        equipment_provider = WizardEquipmentChoicesProvider()
        choices = equipment_provider.get_pack_choices()
        assert choices == {
            duplicate_choice(Pack.Name.SCHOLARS_PACK),
            duplicate_choice(Pack.Name.EXPLORERS_PACK),
        }
