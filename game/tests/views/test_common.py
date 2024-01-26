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
from game.models.events import Event, Quest
from game.models.game import Game, Player
from game.views.common import (
    GameCreateErrorView,
    GameCreateView,
    GameListView,
    GameView,
    IndexView,
)
from master.tests.factories import CampaignFactory
from utils.factories import UserFactory

from ..factories import EventFactory, GameFactory, PlayerFactory, QuestFactory


@pytest.mark.django_db
class TestIndexView:
    path_name = "index"

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
        assertContains(response, "Register")
        assertNotContains(response, "View all games")
        assertNotContains(response, "View all characters")
        assertNotContains(response, "Create a new game")
        assertNotContains(response, "Create a new character")
        assertNotContains(response, "View your character")

    def test_content_logged_user_no_character(self, client):
        user = UserFactory()
        client.force_login(user)

        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assertContains(response, "Log out")
        assertContains(response, "View all games")
        assertContains(response, "View all characters")
        assertContains(response, "Create a new game")
        assertContains(response, "Create a new character")
        assertNotContains(response, "View your character")
        with pytest.raises(KeyError):
            response.context["user_character"]

    def test_content_logged_user_existing_character(self, client):
        character = CharacterFactory()
        client.force_login(character.user)

        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assertContains(response, "Log out")
        assertContains(response, "View all games")
        assertContains(response, "View all characters")
        assertContains(response, "Create a new game")
        assertNotContains(response, "Create a new character")
        assertContains(response, "View your character")
        assert response.context["user_character"] == character


@pytest.fixture(scope="class")
def create_games(django_db_blocker):
    with django_db_blocker.unblock():
        number_of_games = 22
        for _ in range(number_of_games):
            GameFactory(
                start_date=datetime.now(tz=timezone.utc),
                master__user__username="master",
            )


@pytest.mark.django_db
class TestGameListView:
    path_name = "game-list"

    @pytest.fixture(autouse=True)
    def setup(self, client):
        # Only games created by their own master are displayed to them.
        user = UserFactory(username="master")
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
def create_populated_game(django_db_blocker):
    with django_db_blocker.unblock():
        game = GameFactory(master__user__username="master")
        number_of_events = 10
        for _ in range(number_of_events):
            EventFactory(game=game)
        number_of_quests = 3
        for _ in range(number_of_quests):
            QuestFactory(game=game)
        number_of_players = 8
        for _ in range(number_of_players):
            PlayerFactory(game=game)


@pytest.mark.django_db
class TestGameView:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        # Only games created by their own master are displayed to them.
        user = UserFactory(username="master")
        client.force_login(user)
        self.game = Game.objects.last()

    @pytest.fixture(autouse=True)
    def tear_down(self):
        yield cache.clear()

    def test_view_mapping(self, client):
        response = client.get(self.game.get_absolute_url())
        assert response.resolver_match.func.view_class == GameView

    def test_template_mapping(self, client):
        response = client.get(self.game.get_absolute_url())
        assertTemplateUsed(response, "game/game.html")

    def test_pagination_size(self, client, create_populated_game):
        response = client.get(self.game.get_absolute_url())
        assert response.status_code == 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["event_list"]) == 10

    def test_pagination_size_next_page(self, client, create_populated_game):
        response = client.get(self.game.get_absolute_url() + "?page=2")
        assert response.status_code == 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["event_list"]) == 4  # Inherited events

    def test_ordering_character_name_ascending(self, client, create_populated_game):
        response = client.get(self.game.get_absolute_url())
        assert response.status_code == 200
        last_name = ""
        for character in response.context["character_list"]:
            if last_name == "":
                last_name = character.name.upper()
            else:
                assert last_name <= character.name
                last_name = character.name.upper()

    def test_ordering_event_date_descending(self, client, create_populated_game):
        response = client.get(self.game.get_absolute_url())
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

    def test_game_last_quest(self, client):
        quest = Quest.objects.filter(game=self.game).last()
        response = client.get(self.game.get_absolute_url())
        assert response.status_code == 200
        assert response.context["quest"] == quest

    def test_context_data_master(self, client):
        response = client.get(self.game.get_absolute_url())
        assert response.status_code == 200

        quest_list = Quest.objects.filter(game=self.game)
        quest = quest_list.last()
        assert response.context["quest"] == quest
        character_list = Character.objects.filter(player__game=self.game)
        assertQuerySetEqual(
            set(response.context["character_list"]), set(character_list)
        )
        event_list = Event.objects.filter(game=self.game)
        # issubset() is used because of pagination.
        assert set(response.context["event_list"]).issubset(set(event_list))
        with pytest.raises(KeyError):
            response.context["player"]

    def test_context_data_player(self, client):
        client.logout()
        # Log as a player
        character = Character.objects.filter(player__game=self.game).last()
        user = character.user
        client.force_login(user)
        response = client.get(self.game.get_absolute_url())
        assert response.status_code == 200

        quest_list = Quest.objects.filter(game=self.game)
        quest = quest_list.last()
        assert response.context["quest"] == quest
        character_list = Character.objects.filter(player__game=self.game)
        assertQuerySetEqual(
            set(response.context["character_list"]), set(character_list)
        )
        event_list = Event.objects.filter(game=self.game)
        # issubset() is used because of pagination.
        assert set(response.context["event_list"]).issubset(set(event_list))
        player = Player.objects.get(game=self.game, character__user=user)
        assert response.context["player"] == player

    def test_content_character_is_current_user(self, client):
        client.logout()
        # Log as a player
        character = Character.objects.filter(player__game=self.game).last()
        user = character.user
        client.force_login(user)
        response = client.get(self.game.get_absolute_url())
        assert response.status_code == 200
        assertContains(response, "played by you")

    def test_content_no_events(self, client):
        Event.objects.filter(game=self.game).delete()
        response = client.get(self.game.get_absolute_url())
        assert response.status_code == 200
        assertContains(response, "The campaign did not start yet...")


@pytest.mark.django_db
class TestGameCreateView:
    path_name = "game-create"

    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.user = UserFactory(username="user")
        client.force_login(self.user)
        self.campaign = CampaignFactory()

    def test_view_mapping(self, client):
        response = client.get(reverse(self.path_name, args=(self.campaign.slug,)))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == GameCreateView

    def test_template_mapping(self, client):
        response = client.get(reverse(self.path_name, args=(self.campaign.slug,)))
        assert response.status_code == 200
        assertTemplateUsed(response, "game/game_create.html")

    def test_game_creation(self, client):
        response = client.post(reverse(self.path_name, args=(self.campaign.slug,)))
        assert response.status_code == 302
        game = Game.objects.last()
        assertRedirects(response, game.get_absolute_url())
        assert game.name == f"{self.campaign.title} #{game.id}"
        assert game.status == "P"
        assert game.master.user == self.user
        quest = Quest.objects.last()
        assert quest.game == game
        assert quest.message == "The Master created the campaign."
        assert quest.content == self.campaign.synopsis

    def test_game_creation_campaign_does_not_exist(self, client):
        fake = Faker()
        fake_slug = fake.slug()
        response = client.post(reverse(self.path_name, args=(fake_slug,)))
        assert response.status_code == 302
        assertRedirects(response, reverse("game-create-error", args=(fake_slug,)))


@pytest.mark.django_db
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
