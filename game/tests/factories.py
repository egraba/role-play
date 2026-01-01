import random

import factory

from character.constants.abilities import AbilityName
from game.constants.events import DifficultyClass, RollResultType, RollType
from game.models.combat import Combat, Fighter
from game.models.events import (
    CombatInitativeOrderSet,
    CombatInitialization,
    CombatInitiativeRequest,
    CombatInitiativeResponse,
    CombatInitiativeResult,
    Event,
    GameStart,
    Message,
    QuestUpdate,
    RollRequest,
    RollResponse,
    RollResult,
    UserInvitation,
)
from game.models.game import Actor, Game, Master, Player, Quest
from user.tests.factories import UserFactory


class ActorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Actor


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

    @factory.post_generation
    def add_quest(obj, create, extracted, **kwargs):
        if not create:
            return
        QuestFactory(game=obj)


class PlayerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Player
        django_get_or_create = (
            "game",
            "character",
        )

    user = factory.SubFactory(UserFactory)
    game = factory.SubFactory(GameFactory)
    character = factory.SubFactory(
        "character.tests.factories.CharacterFactory", user=user
    )


class QuestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Quest

    environment = factory.Faker("text", max_nb_chars=1000)
    game = factory.SubFactory(GameFactory)


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    game = factory.SubFactory(GameFactory)
    author = factory.SubFactory(ActorFactory)


class GameStartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GameStart

    game = factory.SubFactory(GameFactory)
    author = factory.SubFactory(ActorFactory)


class UserInvitationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserInvitation

    game = factory.SubFactory(GameFactory)
    author = factory.SubFactory(ActorFactory)
    user = factory.SubFactory(UserFactory)


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    game = factory.SubFactory(GameFactory)
    author = factory.SubFactory(ActorFactory)
    content = factory.Faker("text", max_nb_chars=100)


class QuestUpdateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = QuestUpdate

    game = factory.SubFactory(GameFactory)
    author = factory.SubFactory(ActorFactory)
    quest = factory.SubFactory(QuestFactory)


class RollRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RollRequest

    game = factory.SubFactory(GameFactory)
    author = factory.SubFactory(ActorFactory)
    player = factory.SubFactory(PlayerFactory, game=factory.SelfAttribute("..game"))
    ability_type = factory.Faker("enum", enum_cls=AbilityName)
    difficulty_class = factory.Faker("enum", enum_cls=DifficultyClass)
    roll_type = factory.Faker("enum", enum_cls=RollType)


class RollResponseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RollResponse

    game = factory.SubFactory(GameFactory)
    author = factory.SubFactory(ActorFactory)
    request = factory.SubFactory(RollRequest)


class RollResultFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RollResult

    game = factory.SubFactory(GameFactory)
    author = factory.SubFactory(ActorFactory)
    request = factory.SubFactory(RollRequest)
    response = factory.SubFactory(RollResponse)
    score = factory.Faker("random_int", min=1, max=20)
    result = factory.Faker("enum", enum_cls=RollResultType)


class CombatInitalizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CombatInitialization

    game = factory.SubFactory(GameFactory)
    author = factory.SubFactory(ActorFactory)
    combat = factory.SubFactory("game.tests.factories.CombatFactory")


class FighterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Fighter

    player = factory.SubFactory(PlayerFactory)
    character = factory.SubFactory(
        "character.tests.factories.CharacterFactory",
        player=factory.SelfAttribute("..player"),
    )
    combat = factory.SubFactory("game.tests.factories.CombatFactory")


class CombatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Combat
        skip_postgeneration_save = True

    game = factory.SubFactory(GameFactory)

    @factory.post_generation
    def add_fighters(obj, create, extracted, **kwargs):
        if not create:
            return
        for _ in range(random.randint(2, 8)):
            FighterFactory(combat=obj, dexterity_check=random.randint(1, 20))


class CombatInitiativeRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CombatInitiativeRequest

    game = factory.SubFactory(GameFactory)
    author = factory.SubFactory(ActorFactory)
    fighter = factory.SubFactory(FighterFactory)


class CombatInitiativeResponseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CombatInitiativeResponse

    game = factory.SubFactory(GameFactory)
    author = factory.SubFactory(ActorFactory)
    request = factory.SubFactory(CombatInitiativeRequestFactory)


class CombatInitiativeResultFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CombatInitiativeResult

    game = factory.SubFactory(GameFactory)
    author = factory.SubFactory(ActorFactory)
    fighter = factory.SubFactory(FighterFactory)
    request = factory.SubFactory(CombatInitiativeRequestFactory)
    response = factory.SubFactory(CombatInitiativeResponseFactory)
    score = factory.Faker("random_int", min=1, max=20)


class CombatInitativeOrderSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CombatInitativeOrderSet

    game = factory.SubFactory(GameFactory)
    author = factory.SubFactory(ActorFactory)
    combat = factory.SubFactory(CombatFactory)
