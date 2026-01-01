import pytest

from game.models.game import Actor, Game, Master, Player, Quest

from ..factories import (
    ActorFactory,
    GameFactory,
    MasterFactory,
    PlayerFactory,
    QuestFactory,
)

pytestmark = pytest.mark.django_db


class TestGameModel:
    @pytest.fixture
    def game(self):
        return GameFactory(name="game")

    def test_creation(self, game):
        assert isinstance(game, Game)

    def test_str(self, game):
        assert str(game) == game.name


class TestQuestModel:
    @pytest.fixture
    def quest(self):
        return QuestFactory()

    def test_creation(self, quest):
        assert isinstance(quest, Quest)

    def test_str(self, quest):
        assert str(quest) == quest.environment[:10]


class TestActorModel:
    @pytest.fixture
    def actor(self):
        return ActorFactory()

    @pytest.fixture
    def player(self):
        return PlayerFactory()

    @pytest.fixture
    def game(self):
        return GameFactory()

    def test_creation(self, actor):
        assert isinstance(actor, Actor)

    def test_str_returns_username_for_player(self, player):
        actor = Actor.objects.get(pk=player.pk)
        assert str(actor) == player.user.username

    def test_str_returns_username_for_master(self, game):
        actor = Actor.objects.get(pk=game.master.pk)
        assert str(actor) == game.master.user.username

    def test_str_returns_fallback_for_base_actor(self, actor):
        assert str(actor) == f"Actor {actor.pk}"


class MasterModelTest:
    @pytest.fixture
    def master(self):
        return MasterFactory()

    def test_creation(self, master):
        assert isinstance(master, Master)

    def test_str(self, master):
        assert str(master) == master.user.username


class TestPlayerModel:
    @pytest.fixture
    def player(self):
        return PlayerFactory()

    def test_creation(self, player):
        assert isinstance(player, Player)

    def test_str(self, player):
        assert str(player) == player.user.username
