import pytest

from game.models.game import Game, Master, Player

from ..factories import GameFactory, MasterFactory, PlayerFactory


@pytest.mark.django_db
class TestGameModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.game = GameFactory(name="game")

    def test_creation(self):
        assert isinstance(self.game, Game)

    def test_str(self):
        assert str(self.game) == self.game.name

    def test_status_methods(self):
        # Under preparation
        assert self.game.is_under_preparation()
        assert self.game.is_ongoing() is False

        # Ongoing
        number_of_players = 5
        for _ in range(number_of_players):
            PlayerFactory(game=self.game)
        self.game.start()
        self.game.save()
        assert self.game.is_under_preparation() is False
        assert self.game.is_ongoing()


@pytest.mark.django_db
class MasterModelTest:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.master = MasterFactory()

    def test_creation(self):
        assert isinstance(self.master, Master)

    def test_str(self):
        assert str(self.master) == self.master.user.username


@pytest.mark.django_db
class TestPlayerModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.player = PlayerFactory()

    def test_creation(self):
        assert isinstance(self.player, Player)

    def test_str(self):
        assert str(self.player) == self.player.character.user.username
