import pytest
from django.utils import timezone

from game.models.events import Event, QuestUpdate

from ..factories import EventFactory, QuestFactory


@pytest.mark.django_db
class TestEventModel:
    @pytest.fixture
    def event(self):
        return EventFactory()

    def test_creation(self, event):
        assert isinstance(event, Event)
        assert event.date.second - timezone.now().second <= 2


@pytest.mark.django_db
class TestQuestUpdateModel:
    @pytest.fixture
    def quest(self):
        return QuestFactory()

    def test_creation(self, quest):
        assert isinstance(quest, QuestUpdate)

    def test_str(self, quest):
        assert str(quest) == quest.content
