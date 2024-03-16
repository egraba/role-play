from ..models.character import Character
from ..models.races import Language


def get_language_choices(character: Character):
    """
    Return a set of languages to select for a character.
    The set does not include the languages already spoken by the character.
    """
    languages = set(Language.objects.all())
    character_languages = set(character.languages.all())
    return {language for language in languages if language not in character_languages}
