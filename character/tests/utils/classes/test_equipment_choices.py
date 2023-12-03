import pytest

from character.models.equipment import Armor, Gear, Pack, Weapon
from character.utils.classes.equipment_choices import (
    ClericEquipmentChoicesProvider,
    FighterEquipmentChoicesProvider,
    RogueEquipmentChoicesProvider,
    WizardEquipmentChoicesProvider,
)


def enum2textchoice(enum):
    return (enum.value, enum.value)


def enum2textchoice_concat(enum1, enum2):
    return (f"{enum1} & {enum2}", f"{enum1} & {enum2}")


@pytest.mark.django_db
class TestClericEquipmentChoicesProvider:
    def test_get_weapon1_choices(self, equipment):
        equipment_provider = ClericEquipmentChoicesProvider()
        choices = equipment_provider.get_weapon1_choices()
        assert choices == {
            enum2textchoice(Weapon.Name.MACE),
            enum2textchoice(Weapon.Name.WARHAMMER),
        }

    def test_get_weapon2_choices(self, equipment):
        equipment_provider = ClericEquipmentChoicesProvider()
        choices = equipment_provider.get_weapon2_choices()
        assert choices == {
            enum2textchoice(Weapon.Name.CROSSBOW_LIGHT),
            enum2textchoice(Weapon.Name.CLUB),
            enum2textchoice(Weapon.Name.DAGGER),
            enum2textchoice(Weapon.Name.GREATCLUB),
            enum2textchoice(Weapon.Name.HANDAXE),
            enum2textchoice(Weapon.Name.JAVELIN),
            enum2textchoice(Weapon.Name.LIGHT_HAMMER),
            enum2textchoice(Weapon.Name.MACE),
            enum2textchoice(Weapon.Name.QUARTERSTAFF),
            enum2textchoice(Weapon.Name.SICKLE),
            enum2textchoice(Weapon.Name.SPEAR),
            enum2textchoice(Weapon.Name.DART),
            enum2textchoice(Weapon.Name.SHORTBOW),
            enum2textchoice(Weapon.Name.SLING),
        }

    def test_get_weapon3_choices(self, equipment):
        equipment_provider = ClericEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_weapon3_choices()

    def test_get_armor_choices(self, equipment):
        equipment_provider = ClericEquipmentChoicesProvider()
        choices = equipment_provider.get_armor_choices()
        assert choices == {
            enum2textchoice(Armor.Name.SCALE_MAIL),
            enum2textchoice(Armor.Name.LEATHER),
            enum2textchoice(Armor.Name.CHAIN_MAIL),
        }

    def test_get_gear_choices(self, equipment):
        equipment_provider = ClericEquipmentChoicesProvider()
        choices = equipment_provider.get_gear_choices()
        assert choices == {
            enum2textchoice(Gear.Name.AMULET),
            enum2textchoice(Gear.Name.EMBLEM),
            enum2textchoice(Gear.Name.RELIQUARY),
        }

    def test_get_pack_choices(self, equipment):
        equipment_provider = ClericEquipmentChoicesProvider()
        choices = equipment_provider.get_pack_choices()
        assert choices == {
            enum2textchoice(Pack.Name.PRIESTS_PACK),
            enum2textchoice(Pack.Name.EXPLORERS_PACK),
        }


@pytest.mark.django_db
class TestFighterEquipmentChoicesProvider:
    def test_get_weapon1_choices(self, equipment):
        equipment_provider = FighterEquipmentChoicesProvider()
        choices = equipment_provider.get_weapon1_choices()
        assert choices == {
            enum2textchoice(Armor.Name.CHAIN_MAIL),
            enum2textchoice_concat(Armor.Name.LEATHER, Weapon.Name.LONGBOW),
        }

    def test_get_weapon2_choices(self, equipment):
        equipment_provider = FighterEquipmentChoicesProvider()
        choices = equipment_provider.get_weapon2_choices()
        assert choices == {
            enum2textchoice(Weapon.Name.BATTLEAXE),
            enum2textchoice(Weapon.Name.FLAIL),
            enum2textchoice(Weapon.Name.GLAIVE),
            enum2textchoice(Weapon.Name.GREATAXE),
            enum2textchoice(Weapon.Name.GREATSWORD),
            enum2textchoice(Weapon.Name.HALBERD),
            enum2textchoice(Weapon.Name.LANCE),
            enum2textchoice(Weapon.Name.LONGSWORD),
            enum2textchoice(Weapon.Name.MAUL),
            enum2textchoice(Weapon.Name.MORNINGSTAR),
            enum2textchoice(Weapon.Name.PIKE),
            enum2textchoice(Weapon.Name.RAPIER),
            enum2textchoice(Weapon.Name.SCIMITAR),
            enum2textchoice(Weapon.Name.SHORTSWORD),
            enum2textchoice(Weapon.Name.TRIDENT),
            enum2textchoice(Weapon.Name.WAR_PICK),
            enum2textchoice(Weapon.Name.WARHAMMER),
            enum2textchoice(Weapon.Name.WHIP),
            enum2textchoice(Weapon.Name.BLOWGUN),
            enum2textchoice(Weapon.Name.CROSSBOW_HAND),
            enum2textchoice(Weapon.Name.CROSSBOW_HEAVY),
            enum2textchoice(Weapon.Name.LONGBOW),
            enum2textchoice(Weapon.Name.NET),
        }

    def test_get_weapon3_choices(self, equipment):
        equipment_provider = FighterEquipmentChoicesProvider()
        choices = equipment_provider.get_weapon3_choices()
        assert choices == {
            enum2textchoice(Weapon.Name.CROSSBOW_LIGHT),
            enum2textchoice(Weapon.Name.HANDAXE),
        }

    def test_get_armor_choices(self, equipment):
        equipment_provider = FighterEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_armor_choices()

    def test_get_gear_choices(self, equipment):
        equipment_provider = FighterEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_gear_choices()

    def test_get_pack_choices(self, equipment):
        equipment_provider = FighterEquipmentChoicesProvider()
        choices = equipment_provider.get_pack_choices()
        assert choices == {
            enum2textchoice(Pack.Name.DUNGEONEERS_PACK),
            enum2textchoice(Pack.Name.EXPLORERS_PACK),
        }


@pytest.mark.django_db
class TestRogueEquipmentChoicesProvider:
    def test_get_weapon1_choices(self, equipment):
        equipment_provider = RogueEquipmentChoicesProvider()
        choices = equipment_provider.get_weapon1_choices()
        assert choices == {
            enum2textchoice(Weapon.Name.RAPIER),
            enum2textchoice(Weapon.Name.SHORTSWORD),
        }

    def test_get_weapon2_choices(self, equipment):
        equipment_provider = RogueEquipmentChoicesProvider()
        choices = equipment_provider.get_weapon2_choices()
        assert choices == {
            enum2textchoice(Weapon.Name.SHORTBOW),
            enum2textchoice(Weapon.Name.SHORTSWORD),
        }

    def test_get_weapon3_choices(self, equipment):
        equipment_provider = RogueEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_weapon3_choices()

    def test_get_armor_choices(self, equipment):
        equipment_provider = RogueEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_armor_choices()

    def test_get_gear_choices(self, equipment):
        equipment_provider = RogueEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_gear_choices()

    def test_get_pack_choices(self, equipment):
        equipment_provider = RogueEquipmentChoicesProvider()
        choices = equipment_provider.get_pack_choices()
        assert choices == {
            enum2textchoice(Pack.Name.BURGLARS_PACK),
            enum2textchoice(Pack.Name.DUNGEONEERS_PACK),
            enum2textchoice(Pack.Name.EXPLORERS_PACK),
        }


@pytest.mark.django_db
class TestWizardEquipmentChoicesProvider:
    def test_get_weapon1_choices(self, equipment):
        equipment_provider = WizardEquipmentChoicesProvider()
        choices = equipment_provider.get_weapon1_choices()
        assert choices == {
            enum2textchoice(Weapon.Name.QUARTERSTAFF),
            enum2textchoice(Weapon.Name.DAGGER),
        }

    def test_get_weapon2_choices(self, equipment):
        equipment_provider = WizardEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_weapon2_choices()

    def test_get_weapon3_choices(self, equipment):
        equipment_provider = WizardEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_weapon3_choices()

    def test_get_armor_choices(self, equipment):
        equipment_provider = WizardEquipmentChoicesProvider()
        with pytest.raises(NotImplementedError):
            equipment_provider.get_armor_choices()

    def test_get_gear_choices(self, equipment):
        equipment_provider = WizardEquipmentChoicesProvider()
        choices = equipment_provider.get_gear_choices()
        assert choices == {
            enum2textchoice(Gear.Name.COMPONENT_POUCH),
            enum2textchoice(Gear.Name.CRYSTAL),
            enum2textchoice(Gear.Name.ORB),
            enum2textchoice(Gear.Name.ROD),
            enum2textchoice(Gear.Name.STAFF),
            enum2textchoice(Gear.Name.WAND),
        }

    def test_get_pack_choices(self, equipment):
        equipment_provider = WizardEquipmentChoicesProvider()
        choices = equipment_provider.get_pack_choices()
        assert choices == {
            enum2textchoice(Pack.Name.SCHOLARS_PACK),
            enum2textchoice(Pack.Name.EXPLORERS_PACK),
        }
