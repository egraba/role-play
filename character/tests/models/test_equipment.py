from django.db.models import TextChoices
import pytest
from faker import Faker

from character.constants.abilities import AbilityName
from character.constants.equipment import ArmorName, ToolName
from character.models.equipment import (
    ArmorSettings,
    GearSettings,
    Inventory,
    PackSettings,
    ToolSettings,
    WeaponSettings,
)

from ..factories import (
    ArmorFactory,
    ArmorSettingsFactory,
    CharacterFactory,
    GearFactory,
    InventoryFactory,
    PackFactory,
    WeaponFactory,
)


@pytest.mark.django_db
class TestWeaponModel:
    weapon = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.weapon = WeaponSettings.objects.last()

    def test_creation(self):
        assert isinstance(self.weapon, WeaponSettings)

    def test_str(self):
        assert str(self.weapon) == self.weapon.name


@pytest.mark.django_db
class TestArmorModel:
    armor = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.armor = ArmorSettings.objects.last()

    def test_creation(self):
        assert isinstance(self.armor, ArmorSettings)


@pytest.mark.django_db
class TestPackModel:
    pack = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.pack = PackSettings.objects.last()

    def test_creation(self):
        assert isinstance(self.pack, PackSettings)

    def test_str(self):
        assert str(self.pack) == self.pack.name


@pytest.mark.django_db
class TestGearModel:
    gear = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.gear = GearSettings.objects.last()

    def test_creation(self):
        assert isinstance(self.gear, GearSettings)

    def test_str(self):
        assert str(self.gear) == self.gear.name


@pytest.mark.django_db
class TestToolModel:
    tool = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.tool = ToolSettings.objects.last()

    def test_creation(self):
        assert isinstance(self.tool, ToolSettings)

    def test_str(self):
        assert str(self.tool) == self.tool.name


@pytest.mark.django_db
class TestInventoryModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.inventory = InventoryFactory()
        self.inventory.character = CharacterFactory()

    def test_creation(self):
        assert isinstance(self.inventory, Inventory)

    def test_add_armor_simple_ac(self):
        ring_mail_settings = ArmorSettingsFactory(name=ArmorName.RING_MAIL, ac="14")
        ring_mail = ArmorFactory(settings=ring_mail_settings)
        self.inventory.add(ring_mail.settings.name)
        assert self.inventory.character.ac == 14

    def test_add_armor_ac_plus_dex_modifier(self):
        padded_settings = ArmorSettingsFactory(
            name=ArmorName.PADDED, ac="11 + Dex modifier"
        )
        padded = ArmorFactory(settings=padded_settings)
        self.inventory.add(padded.settings.name)
        dex_modifier = self.inventory.character.abilities.get(
            ability_type__name=AbilityName.DEXTERITY
        ).modifier
        assert self.inventory.character.ac == 11 + dex_modifier

    def test_add_armor_ac_plus_dex_modifier_max(self):
        hide_settings = ArmorSettingsFactory(
            name=ArmorName.HIDE, ac="12 + Dex modifier (max 2)"
        )
        hide = ArmorFactory(settings=hide_settings)
        self.inventory.add(hide.settings.name)
        dex_modifier = self.inventory.character.abilities.get(
            ability_type__name=AbilityName.DEXTERITY
        ).modifier
        if dex_modifier > 2:
            assert self.inventory.character.ac == 12 + 2
        else:
            assert self.inventory.character.ac == 12 + dex_modifier

    def test_contains_armor(self):
        armor = ArmorFactory()
        self.inventory.armor_set.add(armor)
        assert self.inventory.contains(armor.settings.name)

    def test_contains_weapon(self):
        weapon = WeaponFactory()
        self.inventory.weapon_set.add(weapon)
        assert self.inventory.contains(weapon.settings.name)

    def test_contains_pack(self):
        pack = PackFactory()
        self.inventory.pack_set.add(pack)
        assert self.inventory.contains(pack.settings.name)

    def test_contains_gear(self):
        gear = GearFactory()
        self.inventory.gear_set.add(gear)
        assert self.inventory.contains(gear.settings.name)

    def test_contains_tool(self):
        fake = Faker()
        tool_name = fake.enum(enum_cls=ToolName)
        self.inventory.add(tool_name)
        assert self.inventory.contains(tool_name)

    def test_contains_unkown_equipment(self):
        class UnknownEquipment(TextChoices):
            UNKNOWN_EQUIPMENT = "unknown_equipment", "Unknown equipment"

        assert not self.inventory.contains(UnknownEquipment.UNKNOWN_EQUIPMENT)

    def test_contains_below_quantity(self):
        weapon = WeaponFactory()
        self.inventory.weapon_set.add(weapon)
        self.inventory.weapon_set.add(weapon)
        assert not self.inventory.contains(weapon.settings.name, 3)

    def test_contains_above_quantity(self):
        weapon = WeaponFactory()
        self.inventory.weapon_set.add(weapon)
        self.inventory.weapon_set.add(weapon)
        assert self.inventory.contains(weapon.settings.name)
