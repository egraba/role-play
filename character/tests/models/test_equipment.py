import pytest
from faker import Faker

from character.constants.abilities import AbilityName
from character.constants.equipment import ArmorName
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
    ToolFactory,
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

    def test_add_armor(self):
        padded_settings = ArmorSettingsFactory(
            name=ArmorName.PADDED, ac="11 + Dex modifier"
        )
        padded = ArmorFactory(settings=padded_settings)
        self.inventory.add(padded.settings.name)
        dex_modifier = self.inventory.character.abilities.get(
            ability_type__name=AbilityName.DEXTERITY
        ).modifier
        assert self.inventory.character.ac == 11 + dex_modifier

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
        tool = ToolFactory()
        self.inventory.tool_set.add(tool)
        assert self.inventory.contains(tool.settings.name)

    def test_contains_unkown_equipment(self):
        fake = Faker()
        assert self.inventory.contains(fake.pystr()) is False
