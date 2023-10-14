import pytest
from pytest_django.asserts import assertTemplateUsed

from character.views.character import CharacterDetailView
from utils.testing.factories import CharacterFactory


@pytest.mark.django_db
class TestChoseEquipmentView:
    character = None

    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.character = CharacterFactory(name="user")
        username = self.character.user.username
        client.login(username=username, password="pwd")

    def test_view_mapping(self, client):
        response = client.get(self.character.get_absolute_url())
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == CharacterDetailView

    def test_template_mapping(self, client):
        response = client.get(self.character.get_absolute_url())
        assert response.status_code == 200
        assertTemplateUsed(response, "character/character.html")
