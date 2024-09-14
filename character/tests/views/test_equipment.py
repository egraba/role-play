import pytest
from django.urls import reverse
from faker import Faker
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from character.constants.equipment import ArmorName, GearName, ToolName, WeaponName
from character.forms.equipment.forms import (
    ClericEquipmentSelectForm,
    FighterEquipmentSelectForm,
    RogueEquipmentSelectForm,
    WizardEquipmentSelectForm,
)
from character.forms.equipment.choices_providers import (
    ClericEquipmentChoicesProvider,
    FighterEquipmentChoicesProvider,
    RogueEquipmentChoicesProvider,
    WizardEquipmentChoicesProvider,
)
from character.views.equipment import EquipmentSelectView


@pytest.mark.django_db
class TestEquipmentSelectView:
    path_name = "equipment-select"

    def test_view_mapping(self, client, character):
        response = client.get(reverse(self.path_name, args=(character.id,)))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == EquipmentSelectView

    def test_template_mapping(self, client, character):
        response = client.get(reverse(self.path_name, args=(character.id,)))
        assert response.status_code == 200
        assertTemplateUsed(response, "character/equipment_select.html")

    def test_cleric_equipment(self, client, cleric):
        equipment_manager = ClericEquipmentChoicesProvider()
        fake = Faker()
        first_weapon = fake.random_element(
            equipment_manager.get_first_weapon_choices()
        )[1]
        second_weapon = fake.random_element(
            equipment_manager.get_second_weapon_choices()
        )[1]
        armor = fake.random_element(equipment_manager.get_armor_choices())[1]
        gear = fake.random_element(equipment_manager.get_gear_choices())[1]
        pack = fake.random_element(equipment_manager.get_pack_choices())[1]
        data = {
            "first_weapon": f"{first_weapon}",
            "second_weapon": f"{second_weapon}",
            "armor": f"{armor}",
            "gear": f"{gear}",
            "pack": f"{pack}",
        }
        form = ClericEquipmentSelectForm(data=data)
        assert form.is_valid()

        character = cleric  # for readability
        response = client.post(
            reverse(self.path_name, args=(character.id,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, character.get_absolute_url())

        inventory = character.inventory
        assert inventory.contains(first_weapon)
        assert inventory.contains(second_weapon)
        assert inventory.contains(armor)
        assert inventory.contains(gear)
        assert inventory.contains(pack)
        assert inventory.contains(ArmorName.SHIELD)

    def test_fighter_equipment(self, client, fighter):
        equipment_manager = FighterEquipmentChoicesProvider()
        fake = Faker()
        first_weapon = fake.random_element(
            equipment_manager.get_first_weapon_choices()
        )[1]
        second_weapon = fake.random_element(
            equipment_manager.get_second_weapon_choices()
        )[1]
        third_weapon = fake.random_element(
            equipment_manager.get_third_weapon_choices()
        )[1]
        pack = fake.random_element(equipment_manager.get_pack_choices())[1]
        data = {
            "first_weapon": f"{first_weapon}",
            "second_weapon": f"{second_weapon}",
            "third_weapon": f"{third_weapon}",
            "pack": f"{pack}",
        }
        form = FighterEquipmentSelectForm(data=data)
        assert form.is_valid()

        character = fighter  # for readability
        response = client.post(
            reverse(self.path_name, args=(character.id,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, character.get_absolute_url())

        inventory = character.inventory
        assert (
            inventory.contains(ArmorName.CHAIN_MAIL)
            or inventory.contains(ArmorName.LEATHER)
            and inventory.contains(WeaponName.LONGBOW)
        )
        assert inventory.contains(second_weapon)
        assert inventory.contains(third_weapon)
        assert inventory.contains(pack)

    def test_rogue_equipment(self, client, rogue):
        equipment_manager = RogueEquipmentChoicesProvider()
        fake = Faker()
        first_weapon = fake.random_element(
            equipment_manager.get_first_weapon_choices()
        )[1]
        second_weapon = fake.random_element(
            equipment_manager.get_second_weapon_choices()
        )[1]
        pack = fake.random_element(equipment_manager.get_pack_choices())[1]
        data = {
            "first_weapon": f"{first_weapon}",
            "second_weapon": f"{second_weapon}",
            "pack": f"{pack}",
        }
        form = RogueEquipmentSelectForm(data=data)
        assert form.is_valid()

        character = rogue  # for readability
        response = client.post(
            reverse(self.path_name, args=(character.id,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, character.get_absolute_url())

        inventory = character.inventory
        assert inventory.contains(first_weapon)
        assert inventory.contains(second_weapon)
        assert inventory.contains(pack)
        assert inventory.contains(ArmorName.LEATHER)
        assert inventory.contains(WeaponName.DAGGER, 2)
        assert inventory.contains(ToolName.THIEVES_TOOLS)

    def test_wizard_equipment(self, client, wizard):
        equipment_manager = WizardEquipmentChoicesProvider()
        fake = Faker()
        first_weapon = fake.random_element(
            equipment_manager.get_first_weapon_choices()
        )[1]
        gear = fake.random_element(equipment_manager.get_gear_choices())[1]
        pack = fake.random_element(equipment_manager.get_pack_choices())[1]
        data = {
            "first_weapon": f"{first_weapon}",
            "gear": f"{gear}",
            "pack": f"{pack}",
        }
        form = WizardEquipmentSelectForm(data=data)
        assert form.is_valid()

        character = wizard  # for readability
        response = client.post(
            reverse(self.path_name, args=(character.id,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, character.get_absolute_url())

        inventory = character.inventory
        assert inventory.contains(first_weapon)
        assert inventory.contains(name=gear)
        assert inventory.contains(name=pack)
        assert inventory.contains(GearName.SPELLBOOK)
