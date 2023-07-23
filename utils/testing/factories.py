import string

import factory
import factory.fuzzy
from django.contrib.auth.models import User

import character.models as cmodels
import game.models as gmodels
import master.models as mmodels


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.fuzzy.FuzzyText()
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

    message = factory.fuzzy.FuzzyText(length=50, chars=string.printable, prefix="event")


class TaleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = gmodels.Tale

    message = factory.fuzzy.FuzzyText(length=50, chars=string.printable, prefix="tale")


class PendingActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = gmodels.PendingAction

    action_type = factory.Sequence(
        lambda n: gmodels.PendingAction.ActionType.choices[n % 2][0]
    )
    message = factory.fuzzy.FuzzyText(
        length=50, chars=string.printable, prefix="pending_action"
    )


class DiceLaunchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = gmodels.DiceLaunch

    score = factory.fuzzy.FuzzyInteger(1, 20)


class CharacterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = cmodels.Character

    name = factory.Sequence(lambda n: f"character{n}")
    user = factory.SubFactory(UserFactory)


class StoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = mmodels.Story
        django_get_or_create = ("title",)

    title = "My story"
