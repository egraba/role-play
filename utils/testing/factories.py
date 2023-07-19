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

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user = model_class(*args, **kwargs)
        user.set_password("pwd")
        user.save()
        return user


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = gmodels.Game

    name = factory.Sequence(lambda n: f"game{n}")


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
