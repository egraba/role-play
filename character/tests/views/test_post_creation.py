import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from character.views.post_creation import EquipmentSelectView
from utils.testing.factories import CharacterFactory


@pytest.mark.django_db
class TestSelectEquipmentView:
    character = None

    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.character = CharacterFactory(name="user")
        user = self.character.user
        client.force_login(user)

    def test_view_mapping(self, client):
        response = client.get(reverse("equipment-select", args=(self.character.id,)))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == EquipmentSelectView

    def test_template_mapping(self, client):
        response = client.get(reverse("equipment-select", args=(self.character.id,)))
        assert response.status_code == 200
        assertTemplateUsed(response, "character/equipment_select.html")
