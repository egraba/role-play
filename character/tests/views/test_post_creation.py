import pytest
from django.urls import reverse
from faker import Faker
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from character.forms.post_creation import EquipmentSelectForm
from character.models.classes import Class
from character.models.equipment import Armor, Equipment, Gear, Tool, Weapon
from character.utils.classes.equipment_choices import (
    ClericEquipmentChoicesProvider,
    FighterEquipmentChoicesProvider,
    RogueEquipmentChoicesProvider,
    WizardEquipmentChoicesProvider,
)
from character.views.post_creation import EquipmentSelectView
from utils.testing.factories import CharacterFactory


@pytest.mark.django_db
class TestEquipmentSelectView:
    path_name = "equipment-select"
    character = None

    @pytest.fixture()
    def setup(self, client):
        self.character = CharacterFactory(name="user")
        user = self.character.user
        client.force_login(user)

    def test_view_mapping(self, client, setup):
        response = client.get(reverse(self.path_name, args=(self.character.id,)))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == EquipmentSelectView

    def test_template_mapping(self, client, setup):
        response = client.get(reverse(self.path_name, args=(self.character.id,)))
        assert response.status_code == 200
        assertTemplateUsed(response, "character/equipment_select.html")

    @pytest.fixture()
    def setup_cleric(self, client):
        self.character = CharacterFactory(name="user", class_name=Class.CLERIC)
        user = self.character.user
        client.force_login(user)

    def test_cleric_equipment(self, client, setup_cleric):
        equipment_manager = ClericEquipmentChoicesProvider()
        fake = Faker()
        weapon1 = fake.random_element(equipment_manager.get_weapon1_choices())[1]
        weapon2 = fake.random_element(equipment_manager.get_weapon2_choices())[1]
        armor = fake.random_element(equipment_manager.get_armor_choices())[1]
        gear = fake.random_element(equipment_manager.get_gear_choices())[1]
        pack = fake.random_element(equipment_manager.get_pack_choices())[1]
        data = {
            "weapon1": f"{weapon1}",
            "weapon2": f"{weapon2}",
            "armor": f"{armor}",
            "gear": f"{gear}",
            "pack": f"{pack}",
        }
        form = EquipmentSelectForm(initial={"class_name": Class.CLERIC}, data=data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name, args=(self.character.id,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, self.character.get_absolute_url())

        inventory = self.character.inventory
        assert Equipment.objects.filter(inventory=inventory, name=weapon1) is not None
        assert Equipment.objects.filter(inventory=inventory, name=weapon2) is not None
        assert Equipment.objects.get(inventory=inventory, name=armor) is not None
        assert Equipment.objects.get(inventory=inventory, name=gear) is not None
        assert Equipment.objects.get(inventory=inventory, name=pack) is not None
        assert (
            Equipment.objects.get(inventory=inventory, name=Armor.Name.SHIELD)
            is not None
        )

    @pytest.fixture()
    def setup_fighter(self, client):
        self.character = CharacterFactory(name="user", class_name=Class.FIGHTER)
        user = self.character.user
        client.force_login(user)

    def test_fighter_equipment(self, client, setup_fighter):
        equipment_manager = FighterEquipmentChoicesProvider()
        fake = Faker()
        weapon1 = fake.random_element(equipment_manager.get_weapon1_choices())[1]
        weapon2 = fake.random_element(equipment_manager.get_weapon2_choices())[1]
        weapon3 = fake.random_element(equipment_manager.get_weapon3_choices())[1]
        pack = fake.random_element(equipment_manager.get_pack_choices())[1]
        data = {
            "weapon1": f"{weapon1}",
            "weapon2": f"{weapon2}",
            "weapon3": f"{weapon3}",
            "pack": f"{pack}",
        }
        form = EquipmentSelectForm(initial={"class_name": Class.FIGHTER}, data=data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name, args=(self.character.id,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, self.character.get_absolute_url())

        inventory = self.character.inventory
        assert Equipment.objects.get(inventory=inventory, name=weapon1) is not None
        assert Equipment.objects.get(inventory=inventory, name=weapon2) is not None
        assert Equipment.objects.get(inventory=inventory, name=weapon3) is not None
        assert Equipment.objects.get(inventory=inventory, name=pack) is not None

    @pytest.fixture()
    def setup_rogue(self, client):
        self.character = CharacterFactory(name="user", class_name=Class.ROGUE)
        user = self.character.user
        client.force_login(user)

    def test_rogue_equipment(self, client, setup_rogue):
        equipment_manager = RogueEquipmentChoicesProvider()
        fake = Faker()
        weapon1 = fake.random_element(equipment_manager.get_weapon1_choices())[1]
        weapon2 = fake.random_element(equipment_manager.get_weapon2_choices())[1]
        pack = fake.random_element(equipment_manager.get_pack_choices())[1]
        data = {
            "weapon1": f"{weapon1}",
            "weapon2": f"{weapon2}",
            "pack": f"{pack}",
        }
        form = EquipmentSelectForm(initial={"class_name": Class.ROGUE}, data=data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name, args=(self.character.id,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, self.character.get_absolute_url())

        inventory = self.character.inventory
        assert Equipment.objects.filter(inventory=inventory, name=weapon1) is not None
        assert Equipment.objects.filter(inventory=inventory, name=weapon2) is not None
        assert Equipment.objects.get(inventory=inventory, name=pack) is not None
        assert (
            Equipment.objects.get(inventory=inventory, name=Armor.Name.LEATHER)
            is not None
        )
        assert (
            Equipment.objects.filter(
                inventory=inventory, name=Weapon.Name.DAGGER
            ).count()
            == 2
        )
        assert (
            Equipment.objects.get(inventory=inventory, name=Tool.Name.THIEVES_TOOLS)
            is not None
        )

    @pytest.fixture()
    def setup_wizard(self, client):
        self.character = CharacterFactory(name="user", class_name=Class.WIZARD)
        user = self.character.user
        client.force_login(user)

    def test_wizard_equipment(self, client, setup_wizard):
        equipment_manager = WizardEquipmentChoicesProvider()
        fake = Faker()
        weapon1 = fake.random_element(equipment_manager.get_weapon1_choices())[1]
        gear = fake.random_element(equipment_manager.get_gear_choices())[1]
        pack = fake.random_element(equipment_manager.get_pack_choices())[1]
        data = {
            "weapon1": f"{weapon1}",
            "gear": f"{gear}",
            "pack": f"{pack}",
        }
        form = EquipmentSelectForm(initial={"class_name": Class.WIZARD}, data=data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name, args=(self.character.id,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, self.character.get_absolute_url())

        inventory = self.character.inventory
        assert Equipment.objects.get(inventory=inventory, name=weapon1) is not None
        assert Equipment.objects.get(inventory=inventory, name=gear) is not None
        assert Equipment.objects.get(inventory=inventory, name=pack) is not None
        assert (
            Equipment.objects.get(inventory=inventory, name=Gear.Name.SPELLBOOK)
            is not None
        )
