import factory

from adventure.models import Campaign
from user.tests.factories import UserFactory


class CampaignFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Campaign
        django_get_or_create = ("title",)

    title = factory.Sequence(lambda n: f"campaign{n}")
    synopsis = factory.Faker("paragraph", nb_sentences=5)
    owner = factory.SubFactory(UserFactory)
