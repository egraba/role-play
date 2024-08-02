import random

import factory

from character.constants.abilities import AbilityName
from game.constants.events import DifficultyClass, RollType
from game.models.combat import Combat, Fighter
from game.models.events import Event, GameStart, QuestUpdate, RollRequest
from game.models.game import Game, Master, Player
from utils.factories import UserFactory


class MasterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Master

    user = factory.SubFactory(UserFactory)


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Game
        skip_postgeneration_save = True

    name = factory.Sequence(lambda n: f"game{n}")
    campaign = factory.SubFactory("master.tests.factories.CampaignFactory")
    master = factory.RelatedFactory(MasterFactory, factory_related_name="game")


class QuestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = QuestUpdate

    game = factory.SubFactory(GameFactory)
    message = "The Master created the campaign."
    content = factory.Faker("paragraph", nb_sentences=10)


class PlayerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Player
        django_get_or_create = (
            "game",
            "character",
        )

    game = factory.SubFactory(GameFactory)
    character = factory.SubFactory("character.tests.factories.CharacterFactory")


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    game = factory.SubFactory(GameFactory)
    message = factory.Faker("text", max_nb_chars=50)


class GameStartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GameStart

    game = factory.SubFactory(GameFactory)


class RollRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RollRequest
        skip_postgeneration_save = True

    game = factory.SubFactory(GameFactory)
    character = factory.SubFactory("character.tests.factories.CharacterFactory")
    ability_type = factory.Faker("enum", enum_cls=AbilityName)
    difficulty_class = factory.Faker("enum", enum_cls=DifficultyClass)
    roll_type = factory.Faker("enum", enum_cls=RollType)

    @factory.post_generation
    def add_character_to_game(obj, create, extracted, **kwargs):
        if not create:
            return
        character = obj.character
        game = obj.game
        PlayerFactory(character=character, game=game)
        character.save()


class FighterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Fighter

    character = factory.SubFactory("character.tests.factories.CharacterFactory")
    combat = factory.SubFactory("game.tests.factories.CombatFactory")


class CombatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Combat
        skip_postgeneration_save = True

    game = factory.SubFactory(GameFactory)
    message = factory.Faker("text", max_nb_chars=50)

    @factory.post_generation
    def add_fighters(obj, create, extracted, **kwargs):
        if not create:
            return
        for _ in range(random.randint(2, 8)):
            FighterFactory(combat=obj, dexterity_check=random.randint(1, 20))
