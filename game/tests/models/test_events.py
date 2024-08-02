import pytest
from django.utils import timezone

from game.models.events import Event, GameStart, QuestUpdate

from ..factories import EventFactory, GameStartFactory, QuestFactory

pytestmark = pytest.mark.django_db


class TestEventModel:
    @pytest.fixture
    def event(self):
        return EventFactory()

    def test_creation(self, event):
        assert isinstance(event, Event)
        assert event.date.second - timezone.now().second <= 2


class TestGameStartModel:
    @pytest.fixture
    def game_start(self):
        return GameStartFactory()

    def test_creation(self, game_start):
        assert isinstance(game_start, GameStart)

    def test_get_message(self, game_start):
        assert game_start.get_message() == "The game started."


class TestQuestUpdateModel:
    @pytest.fixture
    def quest(self):
        return QuestFactory()

    def test_creation(self, quest):
        assert isinstance(quest, QuestUpdate)

    def test_str(self, quest):
        assert str(quest) == quest.content
