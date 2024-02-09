import pytest

from game.models.game import Game, Master, Player

from ..factories import GameFactory, MasterFactory, PlayerFactory


@pytest.mark.django_db
class TestGameModel:
    @pytest.fixture
    def game(self):
        return GameFactory(name="game")

    def test_creation(self, game):
        assert isinstance(game, Game)

    def test_str(self, game):
        assert str(game) == game.name

    def test_status_methods(self, game):
        # Under preparation
        assert game.is_under_preparation()
        assert game.is_ongoing() is False

        # Ongoing
        number_of_players = 5
        for _ in range(number_of_players):
            PlayerFactory(game=game)
        game.start()
        game.save()
        assert game.is_under_preparation() is False
        assert game.is_ongoing()


@pytest.mark.django_db
class MasterModelTest:
    @pytest.fixture
    def master(self):
        return MasterFactory()

    def test_creation(self, master):
        assert isinstance(master, Master)

    def test_str(self, master):
        assert str(master) == master.user.username


@pytest.mark.django_db
class TestPlayerModel:
    @pytest.fixture
    def player(self):
        return PlayerFactory()

    def test_creation(self, player):
        assert isinstance(player, Player)

    def test_str(self, player):
        assert str(player) == player.character.user.username
