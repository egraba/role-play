import factory

from game.models.events import DiceLaunch, Event, Quest
from game.models.game import Game, Master, Player
from utils.dice import Dice
from utils.factories import UserFactory


class MasterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Master

    user = factory.SubFactory(UserFactory)


class QuestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Quest

    message = "The Master created the campaign."
    content = factory.Faker("paragraph", nb_sentences=10)


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Game
        skip_postgeneration_save = True

    name = factory.Sequence(lambda n: f"game{n}")
    campaign = factory.SubFactory("master.tests.factories.CampaignFactory")
    master = factory.RelatedFactory(MasterFactory, factory_related_name="game")
    quest = factory.RelatedFactory(QuestFactory, factory_related_name="game")


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    game = factory.SubFactory(GameFactory)
    message = factory.Faker("text", max_nb_chars=50)


class DiceLaunchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DiceLaunch

    score = Dice("d20").roll()


class PlayerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Player

    game = factory.SubFactory(GameFactory)
    character = factory.SubFactory("character.tests.factories.CharacterFactory")
