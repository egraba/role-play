import factory

from game.models.events import AbilityCheckRequest, Event, Quest
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
        model = Quest

    game = factory.SubFactory(GameFactory)
    message = "The Master created the campaign."
    content = factory.Faker("paragraph", nb_sentences=10)


class PlayerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Player

    game = factory.SubFactory(GameFactory)
    character = factory.SubFactory("character.tests.factories.CharacterFactory")


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    game = factory.SubFactory(GameFactory)
    message = factory.Faker("text", max_nb_chars=50)


class AbilityCheckRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AbilityCheckRequest

    game = factory.SubFactory(GameFactory)
    character = factory.SubFactory("character.tests.factories.CharacterFactory")
    ability_type = factory.SubFactory("character.tests.factories.AbilityTypeFactory")
    difficulty_class = factory.Faker(
        "enum", enum_cls=AbilityCheckRequest.DifficultyClass
    )
