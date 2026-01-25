import pytest
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import RequestFactory

from game.flows import GameFlow
from game.views.mixins import (
    EventContextMixin,
    GameContextMixin,
    GameStatusControlMixin,
)

from ..factories import GameFactory, PlayerFactory


pytestmark = pytest.mark.django_db


class TestGameContextMixin:
    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    @pytest.fixture
    def game(self):
        return GameFactory()

    @pytest.fixture
    def mixin(self):
        """Create a concrete class using the mixin for testing."""

        class TestView(GameContextMixin):
            pass

        return TestView()

    def test_setup_sets_game_attribute(self, mixin, request_factory, game):
        request = request_factory.get("/")
        request.user = game.master.user

        mixin.setup(request, game_id=game.id)

        assert mixin.game == game

    def test_setup_raises_404_for_nonexistent_game(self, mixin, request_factory):
        request = request_factory.get("/")
        request.user = GameFactory().master.user

        with pytest.raises(Http404) as exc_info:
            mixin.setup(request, game_id=99999)

        assert "not found" in str(exc_info.value)

    def test_setup_raises_permission_denied_for_non_participant(
        self, mixin, request_factory, game
    ):
        other_game = GameFactory()
        request = request_factory.get("/")
        request.user = other_game.master.user  # User from different game

        with pytest.raises(PermissionDenied):
            mixin.setup(request, game_id=game.id)

    def test_is_user_master_returns_true_for_master(self, mixin, request_factory, game):
        request = request_factory.get("/")
        request.user = game.master.user

        mixin.setup(request, game_id=game.id)

        assert mixin.is_user_master() is True

    def test_is_user_master_returns_false_for_player(
        self, mixin, request_factory, game
    ):
        player = PlayerFactory(game=game)
        request = request_factory.get("/")
        # Use the character's user since is_user_player checks character__user
        request.user = player.character.user

        mixin.setup(request, game_id=game.id)

        assert mixin.is_user_master() is False

    def test_is_user_player_returns_true_for_player(self, mixin, request_factory, game):
        player = PlayerFactory(game=game)
        request = request_factory.get("/")
        # Use the character's user since is_user_player checks character__user
        request.user = player.character.user

        mixin.setup(request, game_id=game.id)

        assert mixin.is_user_player() is True

    def test_is_user_player_returns_false_for_master(
        self, mixin, request_factory, game
    ):
        request = request_factory.get("/")
        request.user = game.master.user

        mixin.setup(request, game_id=game.id)

        assert mixin.is_user_player() is False

    def test_get_context_data_includes_game(self, mixin, request_factory, game):
        request = request_factory.get("/")
        request.user = game.master.user

        mixin.setup(request, game_id=game.id)
        context = mixin.get_context_data()

        assert "game" in context
        assert context["game"] == game


class TestGameStatusControlMixin:
    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    @pytest.fixture
    def game(self):
        return GameFactory()

    @pytest.fixture
    def mixin(self):
        """Create a concrete class using the mixin for testing."""

        class TestView(GameStatusControlMixin):
            kwargs = {}

            def get_object(self):
                from game.models.game import Game

                return Game.objects.get(pk=self.kwargs.get("pk"))

        return TestView()

    def test_model_is_game(self, mixin):
        from game.models.game import Game

        assert mixin.model == Game

    def test_is_user_master_returns_true_for_master(self, mixin, request_factory, game):
        request = request_factory.get("/")
        request.user = game.master.user
        mixin.request = request
        mixin.kwargs = {"pk": game.pk}

        assert mixin.is_user_master() is True

    def test_is_user_master_returns_false_for_non_master(
        self, mixin, request_factory, game
    ):
        player = PlayerFactory(game=game)
        request = request_factory.get("/")
        request.user = player.user
        mixin.request = request
        mixin.kwargs = {"pk": game.pk}

        assert mixin.is_user_master() is False


class TestEventContextMixin:
    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    @pytest.fixture
    def game(self):
        return GameFactory()

    @pytest.fixture
    def started_game(self, game):
        """Create a game that has been started."""
        # Add enough players to start
        PlayerFactory(game=game)
        PlayerFactory(game=game)
        flow = GameFlow(game)
        flow.start()
        return game

    @pytest.fixture
    def mixin(self):
        """Create a concrete class using the mixin for testing."""

        class TestView(EventContextMixin):
            pass

        return TestView()

    def test_setup_succeeds_for_ongoing_game(
        self, mixin, request_factory, started_game
    ):
        request = request_factory.get("/")
        request.user = started_game.master.user

        # Should not raise
        mixin.setup(request, game_id=started_game.id)
        assert mixin.game == started_game

    def test_setup_raises_permission_denied_for_non_started_game(
        self, mixin, request_factory, game
    ):
        request = request_factory.get("/")
        request.user = game.master.user

        with pytest.raises(PermissionDenied):
            mixin.setup(request, game_id=game.id)

    def test_player_can_send_events_in_ongoing_game(
        self, mixin, request_factory, started_game
    ):
        # Use one of the existing players from the started game
        player = started_game.player_set.first()
        request = request_factory.get("/")
        # Use the character's user since is_user_player checks character__user
        request.user = player.character.user

        # Should not raise
        mixin.setup(request, game_id=started_game.id)
        assert mixin.game == started_game
