from ..models.character import Character
from ..models.races import Language


def get_non_spoken_languages(character: Character):
    """
    Return the set of languages a character does not speak.
    """
    languages = set(Language.objects.all())
    character_languages = set(character.languages.all())
    return {language for language in languages if language not in character_languages}
