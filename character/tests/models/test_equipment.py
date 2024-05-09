import pytest
from faker import Faker

from character.constants.equipment import ArmorName, WeaponName
from character.models.equipment import (
    ArmorSettings,
    GearSettings,
    Inventory,
    PackSettings,
    ToolSettings,
    WeaponSettings,
    Weapon,
)

from ..factories import (
    ArmorFactory,
    ArmorSettingsFactory,
    CharacterFactory,
    InventoryFactory,
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
        assert self.inventory.character.ac == 11

    def test_add_multiple_items(self):
        fake = Faker()
        name1 = fake.random_element(WeaponName.choices[0])
        name2 = fake.random_element(WeaponName.choices[0])
        self.inventory.add(f"{name1} & {name2}")
        assert Weapon.objects.filter(settings__name=name1, inventory=self.inventory)
        assert Weapon.objects.filter(settings__name=name2, inventory=self.inventory)

    def test_contains_armor(self):
        armor = ArmorFactory()
        self.inventory.armor_set.add(armor)
        assert self.inventory.contains(armor.settings.name)
