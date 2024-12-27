import random
from datetime import datetime, timezone

import pytest
from django.core.cache import cache
from django.http import Http404
from django.urls import reverse
from faker import Faker
from pytest_django.asserts import (
    assertContains,
    assertNotContains,
    assertQuerySetEqual,
    assertRedirects,
    assertTemplateUsed,
)

from character.models.character import Character
from character.tests.factories import CharacterFactory
from game.models.events import Event
from game.models.game import Game, Player, Quest
from game.views.common import (
    GameCreateErrorView,
    GameCreateView,
    GameListView,
    GameView,
    IndexView,
)
from master.tests.factories import CampaignFactory
from user.tests.factories import UserFactory

from ..factories import (
    EventFactory,
    GameFactory,
    PlayerFactory,
    QuestUpdateFactory,
    QuestFactory,
)

pytestmark = pytest.mark.django_db


class TestIndexView:
    path_name = "index"

    @pytest.fixture
    def user(self):
        character = CharacterFactory()
        return character.user

    @pytest.fixture
    def user_without_character(self):
        return UserFactory()

    def test_view_mapping(self, client):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == IndexView

    def test_template_mapping(self, client):
        response = client.get(reverse(self.path_name))
        assertTemplateUsed(response, "game/index.html")

    def test_content_anonymous_user(self, client):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assertContains(response, "Log in")
        assertNotContains(response, "Log out")
        assertContains(response, "Register")
        assertNotContains(response, "Create a game")
        assertNotContains(response, "View all games created by you")
        assertNotContains(response, "Continue your character's game")
        assertNotContains(response, "View your character")
        assertNotContains(response, "Create your character")

    def test_content_user_without_character(self, client, user_without_character):
        client.force_login(user_without_character)
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assertNotContains(response, "Log in")
        assertContains(response, "Log out")
        assertNotContains(response, "Register")
        assertContains(response, "Create a game")
        assertContains(response, "View all games created by you")
        assertNotContains(response, "Continue your character's game")
        assertNotContains(response, "View your character")
        assertContains(response, "Create your character")
        assert not response.context["user_has_character"]

    def test_content_user_with_character_no_game(self, client, user):
        client.force_login(user)
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assertNotContains(response, "Log in")
        assertContains(response, "Log out")
        assertNotContains(response, "Register")
        assertContains(response, "Create a game")
        assertContains(response, "View all games created by you")
        assertNotContains(response, "Continue your character's game")
        assertContains(response, "View your character")
        assertNotContains(response, "Create your character")
        assert response.context["user_has_character"]
        assert response.context["user_character"] == user.character

    def test_content_user_with_character_existing_game(self, client, user):
        client.force_login(user)
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        game = GameFactory()
        PlayerFactory(user=user, game=game, character=user.character)
        assertNotContains(response, "Log in")
        assertContains(response, "Log out")
        assertNotContains(response, "Register")
        assertContains(response, "Create a game")
        assertContains(response, "View all games created by you")
        assertContains(response, "Continue your character's game")
        assertContains(response, "View your character")
        assertNotContains(response, "Create your character")
        assert response.context["user_has_character"]
        assert response.context["user_character"] == user.character


@pytest.fixture(scope="class")
def create_games(django_db_blocker):
    with django_db_blocker.unblock():
        number_of_games = 22
        for _ in range(number_of_games):
            GameFactory(
                start_date=datetime.now(tz=timezone.utc),
                master__user__username="master-game-list",
            )


class TestGameListView:
    path_name = "game-list"

    @pytest.fixture(autouse=True)
    def setup(self, client):
        # Only games created by their own master are displayed to them.
        user = UserFactory(username="master-game-list")
        client.force_login(user)

    def test_view_mapping(self, client):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == GameListView

    def test_template_mapping(self, client):
        response = client.get(reverse(self.path_name))
        assertTemplateUsed(response, "game/game_list.html")

    def test_pagination_size(self, client, create_games):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["game_list"]) == 20

    def test_pagination_size_next_page(self, client, create_games):
        response = client.get(reverse(self.path_name) + "?page=2")
        assert response.status_code == 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["game_list"]) == 2

    def test_ordering(self, client, create_games):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        last_date = datetime.now(tz=timezone.utc).second
        for game in response.context["game_list"]:
            if last_date == datetime.now(tz=timezone.utc).second:
                last_date = game.start_date
            else:
                assert last_date >= game.start_date
                last_date = game.start_date

    def test_content_no_game(self, client):
        Game.objects.all().delete()
        response = client.get(reverse(self.path_name))
        assertContains(response, "There is no game available...")


@pytest.fixture(scope="class")
def populated_game(django_db_blocker):
    with django_db_blocker.unblock():
        game = GameFactory(master__user__username="master")
        QuestFactory(game=game)
        number_of_events = 10
        for _ in range(number_of_events):
            EventFactory(game=game)
        number_of_quests = 3
        for _ in range(number_of_quests):
            QuestUpdateFactory(game=game)
        number_of_players = 8
        for _ in range(number_of_players):
            PlayerFactory(game=game)
        return game


class TestGameView:
    @pytest.fixture(autouse=True)
    def login(self, client):
        # Only games created by their own master are displayed to them.
        user = UserFactory(username="master")
        client.force_login(user)

    @pytest.fixture(autouse=True)
    def tear_down(self):
        yield cache.clear()

    def test_view_mapping(self, client, populated_game):
        response = client.get(populated_game.get_absolute_url())
        assert response.resolver_match.func.view_class == GameView

    def test_template_mapping(self, client, populated_game):
        response = client.get(populated_game.get_absolute_url())
        assertTemplateUsed(response, "game/game.html")

    def test_pagination_size(self, client, populated_game):
        response = client.get(populated_game.get_absolute_url())
        assert response.status_code == 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["event_list"]) == 10

    def test_pagination_size_next_page(self, client, populated_game):
        response = client.get(populated_game.get_absolute_url() + "?page=2")
        assert response.status_code == 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["event_list"]) == 3  # Inherited events

    def test_ordering_character_name_ascending(self, client, populated_game):
        response = client.get(populated_game.get_absolute_url())
        assert response.status_code == 200
        last_name = ""
        for character in response.context["character_list"]:
            if last_name == "":
                last_name = character.name.upper()
            else:
                assert last_name <= character.name
                last_name = character.name.upper()

    def test_ordering_event_date_descending(self, client, populated_game):
        response = client.get(populated_game.get_absolute_url())
        assert response.status_code == 200
        last_date = 0
        for event in response.context["event_list"]:
            if last_date == 0:
                last_date = event.date
            else:
                assert last_date >= event.date
                last_date = event.date

    def test_game_not_exists(self, client):
        game_id = random.randint(10000, 99999)
        response = client.get(reverse("game", args=[game_id]))
        assert response.status_code == 404
        assert pytest.raises(Http404)

    def test_game_last_quest(self, client, populated_game):
        quest = Quest.objects.filter(game=populated_game).last()
        response = client.get(populated_game.get_absolute_url())
        assert response.status_code == 200
        assert response.context["quest"] == quest

    def test_context_data_master(self, client, populated_game):
        response = client.get(populated_game.get_absolute_url())
        assert response.status_code == 200

        quest = Quest.objects.filter(game=populated_game).last()
        assert response.context["quest"] == quest
        character_list = Character.objects.filter(player__game=populated_game)
        assertQuerySetEqual(
            set(response.context["character_list"]), set(character_list)
        )
        event_list = Event.objects.filter(game=populated_game).select_subclasses()
        # issubset() is used because of pagination.
        assert set(response.context["event_list"]).issubset(set(event_list))
        with pytest.raises(KeyError):
            response.context["player"]

    def test_context_data_player(self, client, populated_game):
        client.logout()
        # Log as a player
        character = Character.objects.filter(player__game=populated_game).last()
        user = character.user
        client.force_login(user)
        response = client.get(populated_game.get_absolute_url())
        assert response.status_code == 200

        quest = Quest.objects.filter(game=populated_game).last()
        assert response.context["quest"] == quest
        character_list = Character.objects.filter(player__game=populated_game)
        assertQuerySetEqual(
            set(response.context["character_list"]), set(character_list)
        )
        event_list = Event.objects.filter(game=populated_game).select_subclasses()
        # issubset() is used because of pagination.
        assert set(response.context["event_list"]).issubset(set(event_list))
        player = Player.objects.get(game=populated_game, character__user=user)
        assert response.context["player"] == player

    def test_content_character_is_current_user(self, client, populated_game):
        client.logout()
        # Log as a player
        character = Character.objects.filter(player__game=populated_game).last()
        user = character.user
        client.force_login(user)
        response = client.get(populated_game.get_absolute_url())
        assert response.status_code == 200
        assertContains(response, "played by you")

    def test_content_no_events(self, client, populated_game):
        Event.objects.filter(game=populated_game).delete()
        response = client.get(populated_game.get_absolute_url())
        assert response.status_code == 200
        assertContains(response, "The campaign did not start yet...")


class TestGameCreateView:
    path_name = "game-create"

    @pytest.fixture
    def logged_user(self, client):
        user = UserFactory(username="user")
        client.force_login(user)
        return user

    @pytest.fixture
    def campaign(self):
        return CampaignFactory()

    def test_view_mapping(self, client, logged_user, campaign):
        response = client.get(reverse(self.path_name, args=(campaign.slug,)))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == GameCreateView

    def test_template_mapping(self, client, logged_user, campaign):
        response = client.get(reverse(self.path_name, args=(campaign.slug,)))
        assert response.status_code == 200
        assertTemplateUsed(response, "game/game_create.html")

    def test_game_creation(self, client, logged_user, campaign):
        response = client.post(reverse(self.path_name, args=(campaign.slug,)))
        assert response.status_code == 302
        game = Game.objects.last()
        assertRedirects(response, game.get_absolute_url())
        assert game.name == f"{campaign.title} #{game.id}"
        assert game.state == "P"
        assert game.master.user == logged_user
        quest = Quest.objects.filter(game=game).last()
        assert quest.game == game
        assert quest.environment == campaign.synopsis

    def test_game_creation_campaign_does_not_exist(self, client, logged_user):
        fake = Faker()
        fake_slug = fake.slug()
        response = client.post(reverse(self.path_name, args=(fake_slug,)))
        assert response.status_code == 302
        assertRedirects(response, reverse("game-create-error", args=(fake_slug,)))


class TestGameCreateErrorView:
    path_name = "game-create-error"
    fake = Faker()
    fake_slug = fake.slug()

    @pytest.fixture(autouse=True)
    def setup(self, client):
        user = UserFactory(username="user")
        client.force_login(user)

    def test_view_mapping(self, client):
        response = client.get(reverse(self.path_name, args=(self.fake_slug,)))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == GameCreateErrorView

    def test_template_mapping(self, client):
        response = client.get(reverse(self.path_name, args=(self.fake_slug,)))
        assertTemplateUsed(response, "game/game_create_error.html")
