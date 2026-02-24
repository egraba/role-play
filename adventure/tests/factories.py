import factory

from adventure.constants import Difficulty, EncounterType, Region, SceneType
from adventure.models import Act, Campaign, Encounter, Location, NPC, Scene
from user.tests.factories import UserFactory


class CampaignFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Campaign
        django_get_or_create = ("title",)

    title = factory.Sequence(lambda n: f"campaign{n}")
    synopsis = factory.Faker("paragraph", nb_sentences=5)
    owner = factory.SubFactory(UserFactory)


class ActFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Act

    campaign = factory.SubFactory(CampaignFactory)
    title = factory.Sequence(lambda n: f"Act {n}")
    order = factory.Sequence(lambda n: n + 1)
    summary = factory.Faker("paragraph", nb_sentences=3)
    goal = factory.Faker("sentence")


class SceneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Scene

    act = factory.SubFactory(ActFactory)
    title = factory.Sequence(lambda n: f"Scene {n}")
    order = factory.Sequence(lambda n: n + 1)
    scene_type = SceneType.EXPLORATION
    description = factory.Faker("paragraph", nb_sentences=3)
    hook = factory.Faker("sentence")
    resolution = factory.Faker("sentence")


class NPCFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NPC

    campaign = factory.SubFactory(CampaignFactory)
    name = factory.Sequence(lambda n: f"NPC {n}")
    role = "ally"
    motivation = factory.Faker("sentence")
    personality = factory.Faker("sentence")
    appearance = factory.Faker("sentence")


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    campaign = factory.SubFactory(CampaignFactory)
    name = factory.Sequence(lambda n: f"Location {n}")
    description = factory.Faker("paragraph", nb_sentences=2)
    region = Region.DUNGEON


class EncounterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Encounter

    scene = factory.SubFactory(SceneFactory)
    title = factory.Sequence(lambda n: f"Encounter {n}")
    encounter_type = EncounterType.COMBAT
    difficulty = Difficulty.MEDIUM
    description = factory.Faker("paragraph", nb_sentences=2)
