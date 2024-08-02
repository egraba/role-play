import random

import pytest
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from pytest_django.asserts import (
    assertQuerySetEqual,
    assertRedirects,
    assertTemplateUsed,
)

from character.models.character import Character
from character.tests.factories import CharacterFactory
from game.constants.combat import FighterAttributeChoices
from game.flows import GameFlow
from game.forms import CombatCreateForm, QuestCreateForm
from game.models.combat import Combat, Fighter
from game.models.events import Event, QuestUpdate
from game.models.game import Game
from game.views.master import (
    CharacterInviteConfirmView,
    CharacterInviteView,
    CombatCreateView,
    GameStartView,
    QuestCreateView,
)
from utils.factories import UserFactory

from ..factories import GameFactory, PlayerFactory

pytestmark = pytest.mark.django_db


@pytest.fixture(scope="class")
def create_characters(django_db_blocker):
    with django_db_blocker.unblock():
        game = GameFactory(master__user__username="master")
        number_of_characters_in_a_game = 5
        number_of_characters_not_in_a_game = 12
        for _ in range(number_of_characters_in_a_game):
            PlayerFactory(game=game)
        # All characters have to be deleted to avoid pagination issues.
        Character.objects.all().delete()
        for _ in range(number_of_characters_not_in_a_game):
            CharacterFactory()


class TestCharacterInviteView:
    path_name = "game-invite-character"

    @pytest.fixture
    def game(self, client):
        user = UserFactory(username="master")
        client.force_login(user)
        return GameFactory(master__user__username="master")

    def test_view_mapping(self, client, game):
        response = client.get(reverse(self.path_name, args=(game.id,)))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == CharacterInviteView

    def test_template_mapping(self, client, game):
        response = client.get(reverse(self.path_name, args=(game.id,)))
        assert response.status_code == 200
        assertTemplateUsed(response, "game/character_invite.html")

    def test_pagination_size(self, client, game, create_characters):
        response = client.get(reverse(self.path_name, args=(game.id,)))
        assert response.status_code == 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["character_list"]) == 10

    def test_pagination_size_next_page(self, client, game, create_characters):
        response = client.get(reverse(self.path_name, args=(game.id,)) + "?page=2")
        assert response.status_code, 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["character_list"]) == 2

    def test_ordering(self, client, game, create_characters):
        response = client.get(reverse(self.path_name, args=(game.id,)))
        assert response.status_code == 200
        last_xp = 0
        for character in response.context["character_list"]:
            if last_xp == 0:
                last_xp = character.xp
            else:
                assert last_xp >= character.xp
                last_xp = character.xp

    def test_game_not_exists(self, client, game):
        game_id = random.randint(10000, 99999)
        response = client.get(reverse(self.path_name, args=(game_id,)))
        assert response.status_code == 404
        assert pytest.raises(Http404)

    def test_context_data(self, client, game, create_characters):
        character_list = Character.objects.filter(player__game=None)
        response = client.get(reverse(self.path_name, args=(game.id,)))
        assert set(response.context["character_list"]).issubset(character_list)

    def test_context_data_all_characters_already_assigned(self, client, game):
        Character.objects.filter(player=None).delete()
        response = client.get(reverse(self.path_name, args=(game.id,)))
        assertQuerySetEqual(response.context["character_list"], [])


@pytest.fixture(scope="class")
def create_player(django_db_blocker):
    with django_db_blocker.unblock():
        game = GameFactory(master__user__username="master")
        PlayerFactory(game=game)


class TestCharacterInviteConfirmView:
    path_name = "game-invite-character-confirm"

    @pytest.fixture
    def game(self, client, create_player):
        user = User.objects.get(username="master")
        client.force_login(user)
        return GameFactory(master__user__username="master")

    @pytest.fixture
    def character(self):
        return CharacterFactory()

    def test_view_mapping(self, client, game, character):
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    game.id,
                    character.id,
                ),
            )
        )
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == CharacterInviteConfirmView

    def test_template_mapping(self, client, game, character):
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    game.id,
                    character.id,
                ),
            )
        )
        assert response.status_code == 200
        assertTemplateUsed(response, "game/character_invite_confirm.html")

    def test_game_not_exists(self, client, game, character):
        game_id = random.randint(10000, 99999)
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    game_id,
                    character.id,
                ),
            )
        )
        assert response.status_code == 404
        assert pytest.raises(Http404)

    def test_character_added_to_game(self, client, game, character):
        character = CharacterFactory()
        response = client.post(
            reverse(
                self.path_name,
                args=(
                    game.id,
                    character.id,
                ),
            )
        )
        assert response.status_code == 302
        assertRedirects(response, reverse("game", args=(game.id,)))
        assert character.player.game == game
        event = Event.objects.last()
        assert event.date.second - timezone.now().second <= 2
        assert event.game == game
        assert event.message == f"{character} was added to the game."


class TestGameStartView:
    path_name = "game-start"

    @pytest.fixture
    def game(self, client, create_player):
        user = User.objects.get(username="master")
        client.force_login(user)
        return GameFactory(master__user__username="master")

    @pytest.fixture
    def character(self, game):
        return Character.objects.get(player__game=game)

    def test_view_mapping(self, client, game):
        response = client.get(reverse(self.path_name, args=(game.id,)))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == GameStartView

    def test_template_mapping(self, client, game):
        response = client.get(reverse(self.path_name, args=(game.id,)))
        assert response.status_code == 200
        assertTemplateUsed(response, "game/game_start.html")

    def test_game_not_exists(self, client, game):
        game_id = random.randint(10000, 99999)
        response = client.get(reverse(self.path_name, args=(game_id,)))
        assert response.status_code == 404
        assert pytest.raises(Http404)

    def test_game_start_ok(self, client, game):
        number_of_players = 2
        for _ in range(number_of_players):
            PlayerFactory(game=game)
        response = client.post(reverse(self.path_name, args=(game.id,)))
        assert response.status_code == 302
        # Need to query the game again.
        game = Game.objects.last()
        flow = GameFlow(game)
        assert flow.is_ongoing()
        assert game.start_date.second - timezone.now().second <= 2
        event = Event.objects.last()
        assert event.date.second - timezone.now().second <= 2
        assert event.game == game
        assert event.message == "the game started."

    def test_game_start_not_enough_characters(self, client, game):
        PlayerFactory(game=game)
        response = client.post(reverse(self.path_name, args=(game.id,)))
        assert response.status_code == 302
        assert pytest.raises(PermissionDenied)
        flow = GameFlow(game)
        assert flow.is_under_preparation()
        assertRedirects(response, reverse("game-start-error", args=(game.id,)))


@pytest.fixture(scope="class")
def started_game(django_db_blocker):
    with django_db_blocker.unblock():
        game = GameFactory(master__user__username="master")
        number_of_players = 3
        for _ in range(number_of_players):
            PlayerFactory(game=game)
        flow = GameFlow(game)
        flow.start()
        return game


class TestQuestCreateView:
    path_name = "quest-create"

    @pytest.fixture
    def login(self, client):
        user = User.objects.get(username="master")
        client.force_login(user)

    @pytest.fixture(autouse=True)
    def tear_down(self):
        yield cache.clear()

    def test_view_mapping(self, client, login, started_game):
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == QuestCreateView

    def test_template_mapping(self, client, login, started_game):
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert response.status_code == 200
        assertTemplateUsed(response, "game/quest_create.html")

    def test_game_not_exists(self, client, login):
        game_id = random.randint(10000, 99999)
        response = client.get(reverse(self.path_name, args=(game_id,)))
        assert response.status_code == 404
        assert pytest.raises(Http404)

    def test_context_data(self, client, login, started_game):
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert response.status_code == 200
        assert response.context["game"] == started_game

    def test_game_is_under_preparation(self, client, login, started_game):
        started_game.state = "P"
        started_game.save()
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert response.status_code == 403
        assert pytest.raises(PermissionDenied)

    def test_quest_creation(self, client, login, started_game):
        fake = Faker()
        content = fake.text(100)
        data = {"content": f"{content}"}
        form = QuestCreateForm(data)
        assert form.is_valid()
        response = client.post(
            reverse(self.path_name, args=(started_game.id,)), data=form.cleaned_data
        )
        assert response.status_code == 302
        quest_update = QuestUpdate.objects.filter(game=started_game).last()
        assert quest_update.game == started_game
        assert quest_update.message == "the Master updated the campaign."
        assert quest_update.content == form.cleaned_data["content"]
        assertRedirects(response, started_game.get_absolute_url())


class TestCombatCreateView:
    path_name = "combat-create"

    @pytest.fixture(autouse=True)
    def login(self, client):
        user = User.objects.get(username="master")
        client.force_login(user)

    def test_view_mapping(self, client, started_game):
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == CombatCreateView

    def test_template_mapping(self, client, started_game):
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert response.status_code == 200
        assertTemplateUsed(response, "game/combat_create.html")

    def test_form_valid_combat_and_fighters_created(self, client, started_game):
        characters = Character.objects.filter(player__game=started_game)
        data = {}
        data[characters.first().name] = [FighterAttributeChoices.IS_FIGHTING]
        data[characters.last().name] = [FighterAttributeChoices.IS_FIGHTING]
        form = CombatCreateForm(data, initial={"game": f"{started_game.id}"})
        assert form.is_valid()
        response = client.post(
            reverse(self.path_name, args=(started_game.id,)), data=form.cleaned_data
        )
        assert response.status_code == 302
        assertRedirects(response, started_game.get_absolute_url())
        combat = Combat.objects.filter(game=started_game).last()
        assert combat
        assert list(combat.fighter_set.all()) == [
            Fighter.objects.get(character=characters.first()),
            Fighter.objects.get(character=characters.last()),
        ]
