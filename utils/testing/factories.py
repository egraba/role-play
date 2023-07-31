import random

import factory
from django.contrib.auth.models import User

import character.models as cmodels
import game.models as gmodels
import master.models as mmodels


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Faker("profile", fields=["username"])
    password = factory.django.Password("pwd")


class MasterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = gmodels.Master

    user = factory.SubFactory(UserFactory)


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = gmodels.Game

    name = factory.Sequence(lambda n: f"game{n}")
    master = factory.RelatedFactory(MasterFactory, factory_related_name="game")


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = gmodels.Event

    message = factory.Faker("text", max_nb_chars=50)


class TaleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = gmodels.Tale

    message = factory.Faker("text", max_nb_chars=50)


class PendingActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = gmodels.PendingAction

    action_type = factory.Sequence(
        lambda n: gmodels.PendingAction.ActionType.choices[n % 2][0]
    )
    message = factory.Faker("text", max_nb_chars=50)


class DiceLaunchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = gmodels.DiceLaunch

    score = factory.Faker("random_int", min=1, max=20)


class CharacterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = cmodels.Character

    name = factory.Sequence(lambda n: f"character{n}")
    user = factory.SubFactory(UserFactory)
    race = random.choice(cmodels.Character.Race.choices)[0]


class PlayerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = gmodels.Player

    character = factory.SubFactory(CharacterFactory)


class StoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = mmodels.Story
        django_get_or_create = ("title",)

    title = factory.Sequence(lambda n: f"story{n}")
