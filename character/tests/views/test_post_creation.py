import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from character.forms.post_creation import SelectEquipmentForm
from character.models.classes import Class
from character.models.equipment import Armor, Equipment, Pack, Weapon
from character.views.post_creation import EquipmentSelectView
from utils.testing.factories import CharacterFactory


@pytest.mark.django_db
class TestSelectEquipmentView:
    path_name = "equipment-select"
    character = None

    @pytest.fixture()
    def setup(self, client, equipment):
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
    def setup_cleric(self, client, equipment):
        self.character = CharacterFactory(name="user", class_name=Class.CLERIC)
        user = self.character.user
        client.force_login(user)

    def test_cleric_equipment(self, client, setup_cleric):
        data = {
            "weapon1": f"{Weapon.Name.MACE}",
            "weapon2": f"{Weapon.Name.CROSSBOW_LIGHT}",
            "armor": f"{Armor.Name.SCALE_MAIL}",
            "pack": f"{Pack.Name.EXPLORERS_PACK}",
        }
        form = SelectEquipmentForm(initial={"class_name": Class.CLERIC}, data=data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name, args=(self.character.id,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, self.character.get_absolute_url())

        assert (
            Equipment.objects.get(
                inventory=self.character.inventory, name=Weapon.Name.MACE
            )
            is not None
        )
        assert (
            Equipment.objects.get(
                inventory=self.character.inventory, name=Weapon.Name.CROSSBOW_LIGHT
            )
            is not None
        )
        assert (
            Equipment.objects.get(
                inventory=self.character.inventory, name=Armor.Name.SCALE_MAIL
            )
            is not None
        )
        assert (
            Equipment.objects.get(
                inventory=self.character.inventory, name=Pack.Name.EXPLORERS_PACK
            )
            is not None
        )
        assert (
            Equipment.objects.get(
                inventory=self.character.inventory, name=Armor.Name.SHIELD
            )
            is not None
        )
