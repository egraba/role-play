import pytest
from django.http import Http404
from django.test import RequestFactory
from django.views.generic import TemplateView
from faker import Faker

from character.views.mixins import CharacterContextMixin

pytestmark = pytest.mark.django_db


class TestCharacterContextMixin:
    class MyView(CharacterContextMixin, TemplateView):
        pass

    @pytest.fixture
    def http_request(self):
        factory = RequestFactory()
        return factory.get("/")

    def test_character_exists(self, http_request, character):
        view = self.MyView()
        view.setup(http_request, character_id=character.id)
        context = view.get_context_data()
        assert context["character"] == character

    def test_character_does_not_exist(self, http_request):
        fake = Faker()
        view = self.MyView()
        with pytest.raises(Http404):
            view.setup(http_request, character_id=fake.random_int(min=1000, max=9999))
