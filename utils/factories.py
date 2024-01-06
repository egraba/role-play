import factory
from django.contrib.auth.models import User

from character.models.character import Character
from character.models.classes import Class
from character.models.races import Race
from game.models import DiceLaunch, Event, Game, Master, Player, Quest
from master.models import Campaign
from utils.dice import Dice


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Faker("user_name")
    email = factory.Faker("email")


class MasterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Master

    user = factory.SubFactory(UserFactory)


class CampaignFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Campaign
        django_get_or_create = ("title",)

    title = factory.Sequence(lambda n: f"campaign{n}")
    synopsis = factory.Faker("paragraph", nb_sentences=10)


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
    campaign = factory.SubFactory(CampaignFactory)
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


class CharacterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Character
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"character{n}")
    user = factory.SubFactory(UserFactory)
    race = factory.Faker("enum", enum_cls=Race)
    class_name = factory.Faker("enum", enum_cls=Class)
    xp = factory.Faker("random_int")


class PlayerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Player

    game = factory.SubFactory(GameFactory)
    character = factory.SubFactory(CharacterFactory)
