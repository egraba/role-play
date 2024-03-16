import pytest
from faker import Faker

from ..factories import CharacterFactory
from character.constants.races import LanguageName
from character.models.races import Language
from character.utils.backgrounds import get_language_choices


@pytest.mark.django_db
def test_get_language_choices():
    character = CharacterFactory()
    fake = Faker()
    character.languages.add(Language.objects.get(name=fake.enum(enum_cls=LanguageName)))
    character.languages.add(Language.objects.get(name=fake.enum(enum_cls=LanguageName)))
    character_languages = set(character.languages.all())
    language_choices = get_language_choices(character)
    assert character_languages & language_choices == set()
    languages = set(Language.objects.all())
    assert language_choices < languages
