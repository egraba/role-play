import pytest

from character.models.equipment import Armor, Equipment, Gear, Pack, Tool, Weapon

from ..factories import EquipmentFactory


@pytest.mark.django_db
class TestEquipmentModel:
    equipment = None

    @pytest.fixture(autouse=True)
    def setup(self):
        self.equipment = EquipmentFactory()

    def test_creation(self):
        assert isinstance(self.equipment, Equipment)

    def test_str(self):
        assert str(self.equipment) == self.equipment.name


@pytest.mark.django_db
class TestWeaponModel:
    weapon = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.weapon = Weapon.objects.last()

    def test_creation(self):
        assert isinstance(self.weapon, Weapon)

    def test_str(self):
        assert str(self.weapon) == self.weapon.name


@pytest.mark.django_db
class TestArmorModel:
    armor = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.armor = Armor.objects.last()

    def test_creation(self):
        assert isinstance(self.armor, Armor)

    def test_str(self):
        assert str(self.armor) == self.armor.name


@pytest.mark.django_db
class TestPackModel:
    pack = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.pack = Pack.objects.last()

    def test_creation(self):
        assert isinstance(self.pack, Pack)

    def test_str(self):
        assert str(self.pack) == self.pack.name


@pytest.mark.django_db
class TestGearModel:
    gear = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.gear = Gear.objects.last()

    def test_creation(self):
        assert isinstance(self.gear, Gear)

    def test_str(self):
        assert str(self.gear) == self.gear.name


@pytest.mark.django_db
class TestToolModel:
    tool = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.tool = Tool.objects.last()

    def test_creation(self):
        assert isinstance(self.tool, Tool)

    def test_str(self):
        assert str(self.tool) == self.tool.name
