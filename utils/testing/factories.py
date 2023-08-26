import dice
import factory
from django.contrib.auth.models import User

import character.models as cmodels
import game.models as gmodels
import master.models as mmodels


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Faker("user_name")
    password = factory.django.Password("pwd")
    email = factory.Faker("email")


class MasterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = gmodels.Master

    user = factory.SubFactory(UserFactory)


class StoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = mmodels.Story
        django_get_or_create = ("title",)

    title = factory.Sequence(lambda n: f"story{n}")
    synopsis = factory.Faker("paragraph", nb_sentences=10)


class TaleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = gmodels.Tale

    message = "The Master created the story."
    content = factory.Faker("paragraph", nb_sentences=10)


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = gmodels.Game

    name = factory.Sequence(lambda n: f"game{n}")
    story = factory.SubFactory(StoryFactory)
    master = factory.RelatedFactory(MasterFactory, factory_related_name="game")
    tale = factory.RelatedFactory(TaleFactory, factory_related_name="game")


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = gmodels.Event

    message = factory.Faker("text", max_nb_chars=50)


class DiceLaunchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = gmodels.DiceLaunch

    score = dice.roll("d20")


class CharacterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = cmodels.Character
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"character{n}")
    user = factory.SubFactory(UserFactory)
    race = factory.Faker("enum", enum_cls=cmodels.Character.Race)
    xp = factory.Faker("random_int")


class PlayerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = gmodels.Player

    character = factory.SubFactory(CharacterFactory)
