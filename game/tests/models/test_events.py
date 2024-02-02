import pytest
from django.utils import timezone

from game.models.events import Event, Quest

from ..factories import EventFactory, GameFactory


@pytest.mark.django_db
class TestEventModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.event = EventFactory()

    def test_creation(self):
        assert isinstance(self.event, Event)
        assert self.event.date.second - timezone.now().second <= 2

    def test_str(self):
        assert str(self.event) == self.event.message


@pytest.mark.django_db
class TestQuestModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        game = GameFactory()
        self.quest = Quest.objects.filter(game=game).last()

    def test_creation(self):
        assert isinstance(self.quest, Quest)

    def test_str(self):
        assert str(self.quest) == self.quest.content
