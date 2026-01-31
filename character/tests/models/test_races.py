import pytest

from character.models.races import Language


@pytest.mark.django_db
class TestLanguageModel:
    def test_creation(self):
        language, _ = Language.objects.get_or_create(
            name="common",
            defaults={"language_type": "S"},
        )
        assert isinstance(language, Language)

    def test_str(self):
        language, _ = Language.objects.get_or_create(
            name="elvish",
            defaults={"language_type": "S"},
        )
        assert str(language) == language.name
