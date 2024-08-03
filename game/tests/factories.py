import factory

from character.constants.abilities import AbilityName
from game.constants.events import DifficultyClass, RollResultType, RollType
from game.models.events import (
    CharacterInvitation,
    Event,
    GameStart,
    Message,
    QuestUpdate,
    RollRequest,
    RollResponse,
    RollResult,
)
from game.models.game import Game, Master, Player
from utils.factories import UserFactory


class MasterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Master

    user = factory.SubFactory(UserFactory)


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Game

    name = factory.Sequence(lambda n: f"game{n}")
    campaign = factory.SubFactory("master.tests.factories.CampaignFactory")
    master = factory.RelatedFactory(MasterFactory, factory_related_name="game")


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


class GameStartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GameStart

    game = factory.SubFactory(GameFactory)


class CharacterInvitationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CharacterInvitation

    game = factory.SubFactory(GameFactory)
    character = factory.SubFactory("character.tests.factories.CharacterFactory")


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    game = factory.SubFactory(GameFactory)
    content = factory.Faker("text", max_nb_chars=100)
    is_from_master = factory.Faker("boolean")


class QuestUpdateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = QuestUpdate

    game = factory.SubFactory(GameFactory)
    content = factory.Faker("paragraph", nb_sentences=10)


class RollRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RollRequest

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


class RollResponseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RollResponse

    game = factory.SubFactory(GameFactory)
    character = factory.SubFactory("character.tests.factories.CharacterFactory")
    request = factory.SubFactory(RollRequest)


class RollResultFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RollResult

    game = factory.SubFactory(GameFactory)
    character = factory.SubFactory("character.tests.factories.CharacterFactory")
    request = factory.SubFactory(RollRequest)
    response = factory.SubFactory(RollResponse)
    score = factory.Faker("random_int", min=1, max=20)
    result = factory.Faker("enum", enum_cls=RollResultType)
