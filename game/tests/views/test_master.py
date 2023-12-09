import random

import pytest
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.forms import ValidationError
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
from game.forms import CreateQuestForm, DamageForm, HealForm, IncreaseXpForm
from game.models import Damage, Event, Game, Healing, Quest, XpIncrease
from game.views.master import (
    CharacterInviteConfirmView,
    CharacterInviteView,
    DamageView,
    GameStartView,
    HealingView,
    QuestCreateView,
    XpIncreaseView,
)
from utils.testing.factories import (
    CharacterFactory,
    GameFactory,
    PlayerFactory,
    UserFactory,
)


@pytest.fixture(scope="class")
def create_characters(django_db_blocker):
    with django_db_blocker.unblock():
        game = GameFactory(master__user__username="master")
        number_of_characters_in_a_game = 5
        number_of_characters_not_in_a_game = 12
        for i in range(number_of_characters_in_a_game):
            PlayerFactory(game=game)
        # All characters have to be deleted to avoid pagination issues.
        Character.objects.all().delete()
        for i in range(number_of_characters_not_in_a_game):
            CharacterFactory()


@pytest.mark.django_db
class TestCharacterInviteView:
    path_name = "game-invite-character"

    @pytest.fixture(autouse=True)
    def setup(self, client):
        user = UserFactory(username="master")
        client.force_login(user)
        self.game = GameFactory(master__user__username="master")

    def test_view_mapping(self, client):
        response = client.get(reverse(self.path_name, args=(self.game.id,)))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == CharacterInviteView

    def test_template_mapping(self, client):
        response = client.get(reverse(self.path_name, args=(self.game.id,)))
        assert response.status_code == 200
        assertTemplateUsed(response, "game/character_invite.html")

    def test_pagination_size(self, client, create_characters):
        response = client.get(reverse(self.path_name, args=(self.game.id,)))
        assert response.status_code == 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["character_list"]) == 10

    def test_pagination_size_next_page(self, client, create_characters):
        response = client.get(reverse(self.path_name, args=(self.game.id,)) + "?page=2")
        assert response.status_code, 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["character_list"]) == 2

    def test_ordering(self, client, create_characters):
        response = client.get(reverse(self.path_name, args=(self.game.id,)))
        assert response.status_code == 200
        last_xp = 0
        for character in response.context["character_list"]:
            if last_xp == 0:
                last_xp = character.xp
            else:
                assert last_xp >= character.xp
                last_xp = character.xp

    def test_game_not_exists(self, client):
        game_id = random.randint(10000, 99999)
        response = client.get(reverse(self.path_name, args=(game_id,)))
        assert response.status_code == 404
        assert pytest.raises(Http404)

    def test_context_data(self, client, create_characters):
        character_list = Character.objects.filter(player__game=None)
        response = client.get(reverse(self.path_name, args=(self.game.id,)))
        assert set(response.context["character_list"]).issubset(character_list)

    def test_context_data_all_characters_already_assigned(self, client):
        Character.objects.filter(player=None).delete()
        response = client.get(reverse(self.path_name, args=(self.game.id,)))
        assertQuerySetEqual(response.context["character_list"], [])


@pytest.fixture(scope="class")
def create_player(django_db_blocker):
    with django_db_blocker.unblock():
        game = GameFactory(master__user__username="master")
        PlayerFactory(game=game)


@pytest.mark.django_db
class TestCharacterInviteConfirmView:
    path_name = "game-invite-character-confirm"

    @pytest.fixture(autouse=True)
    def setup(self, client, create_player):
        user = User.objects.get(username="master")
        client.force_login(user)
        self.game = Game.objects.last()
        self.character = Character.objects.get(player__game=self.game)

    def test_view_mapping(self, client):
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == CharacterInviteConfirmView

    def test_template_mapping(self, client):
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        assert response.status_code == 200
        assertTemplateUsed(response, "game/character_invite_confirm.html")

    def test_game_not_exists(self, client):
        game_id = random.randint(10000, 99999)
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    game_id,
                    self.character.id,
                ),
            )
        )
        assert response.status_code == 404
        assert pytest.raises(Http404)

    def test_character_added_to_game(self, client):
        character = CharacterFactory()
        response = client.post(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    character.id,
                ),
            )
        )
        assert response.status_code == 302
        assertRedirects(response, reverse("game", args=(self.game.id,)))
        assert self.character.player.game == self.game
        event = Event.objects.last()
        assert event.date.second - timezone.now().second <= 2
        assert event.game == self.game
        assert event.message == f"{character} was added to the game."


@pytest.fixture(scope="class")
def create_game(django_db_blocker):
    with django_db_blocker.unblock():
        GameFactory(master__user__username="master")


@pytest.mark.django_db
class TestGameStartView:
    path_name = "game-start"

    @pytest.fixture(autouse=True)
    def setup(self, client):
        user = User.objects.get(username="master")
        client.force_login(user)
        self.game = Game.objects.last()

    def test_view_mapping(self, client):
        response = client.get(reverse(self.path_name, args=(self.game.id,)))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == GameStartView

    def test_template_mapping(self, client):
        response = client.get(reverse(self.path_name, args=(self.game.id,)))
        assert response.status_code == 200
        assertTemplateUsed(response, "game/game_start.html")

    def test_game_not_exists(self, client):
        game_id = random.randint(10000, 99999)
        response = client.get(reverse(self.path_name, args=(game_id,)))
        assert response.status_code == 404
        assert pytest.raises(Http404)

    def test_game_start_ok(self, client, create_game):
        number_of_players = 2
        for _ in range(number_of_players):
            PlayerFactory(game=self.game)
        response = client.post(reverse(self.path_name, args=(self.game.id,)))
        assert response.status_code == 302
        # Need to query the game again.
        self.game = Game.objects.last()
        assert self.game.is_ongoing()
        assert self.game.start_date.second - timezone.now().second <= 2
        event = Event.objects.last()
        assert event.date.second - timezone.now().second <= 2
        assert event.game == self.game
        assert event.message == "the game started."

    def test_game_start_not_enough_characters(self, client, create_game):
        PlayerFactory(game=self.game)
        response = client.post(reverse(self.path_name, args=(self.game.id,)))
        assert response.status_code == 302
        assert pytest.raises(PermissionDenied)
        assert self.game.is_under_preparation()
        assertRedirects(response, reverse("game-start-error", args=(self.game.id,)))


@pytest.fixture(scope="class")
def create_game_and_start(django_db_blocker):
    with django_db_blocker.unblock():
        game = GameFactory(master__user__username="master")
        number_of_players = 3
        for _ in range(number_of_players):
            PlayerFactory(game=game)
        game.start()
        game.save()


@pytest.mark.django_db
class TestQuestCreateView:
    path_name = "quest-create"

    @pytest.fixture(autouse=True)
    def setup(self, client, create_game_and_start):
        user = User.objects.get(username="master")
        client.force_login(user)
        self.game = Game.objects.last()
        self.character = Character.objects.last()

    @pytest.fixture(autouse=True)
    def tear_down(self):
        yield cache.clear()

    def test_view_mapping(self, client):
        response = client.get(reverse(self.path_name, args=(self.game.id,)))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == QuestCreateView

    def test_template_mapping(self, client):
        response = client.get(reverse(self.path_name, args=(self.game.id,)))
        assert response.status_code == 200
        assertTemplateUsed(response, "game/quest_create.html")

    def test_game_not_exists(self, client):
        game_id = random.randint(10000, 99999)
        response = client.get(reverse(self.path_name, args=(game_id,)))
        assert response.status_code == 404
        assert pytest.raises(Http404)

    def test_context_data(self, client):
        response = client.get(reverse(self.path_name, args=(self.game.id,)))
        assert response.status_code == 200
        assert response.context["game"] == self.game

    def test_game_is_under_preparation(self, client):
        self.game.status = "P"
        self.game.save()
        response = client.get(reverse(self.path_name, args=(self.game.id,)))
        assert response.status_code == 403
        assert pytest.raises(PermissionDenied)

    def test_quest_creation(self, client):
        fake = Faker()
        content = fake.text(100)
        data = {"content": f"{content}"}
        form = CreateQuestForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name, args=(self.game.id,)), data=form.cleaned_data
        )
        assert response.status_code == 302
        quest = Quest.objects.filter(game=self.game).last()
        assert quest.game == self.game
        assert quest.message == "the Master updated the campaign."
        assert quest.content == form.cleaned_data["content"]
        assertRedirects(response, self.game.get_absolute_url())


@pytest.mark.django_db
class TestXpIncreaseView:
    path_name = "xpincrease-create"

    @pytest.fixture(autouse=True)
    def setup(self, client):
        user = User.objects.get(username="master")
        client.force_login(user)
        self.game = Game.objects.last()
        self.character = Character.objects.last()

    @pytest.fixture(autouse=True)
    def tear_down(self):
        yield cache.clear()

    def test_view_mapping(self, client):
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == XpIncreaseView

    def test_template_mapping(self, client):
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        assert response.status_code == 200
        assertTemplateUsed(response, "game/xp.html")

    def test_game_not_exists(self, client):
        game_id = random.randint(10000, 99999)
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    game_id,
                    self.character.id,
                ),
            )
        )
        assert response.status_code == 404
        assert pytest.raises(Http404)

    def test_character_not_exists(self, client):
        character_id = random.randint(10000, 99999)
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    character_id,
                ),
            )
        )
        assert response.status_code == 404
        assert pytest.raises(Http404)

    def test_context_data(self, client):
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        assert response.status_code == 200
        assert response.context["game"] == self.game
        assert response.context["character"] == self.character

    def test_game_is_under_preparation(self, client):
        self.game.status = "P"
        self.game.save()
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        assert response.status_code == 403
        assert pytest.raises(PermissionDenied)

    def test_creation_ok(self, client):
        xp = random.randint(1, 20)
        data = {"xp": f"{xp}"}
        form = IncreaseXpForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            ),
            data=form.cleaned_data,
        )
        assert response.status_code, 302
        xp_increase = XpIncrease.objects.last()
        assert xp_increase.game == self.game
        assert xp_increase.character == self.character
        assert xp_increase.date.second - timezone.now().second <= 2
        assert (
            xp_increase.message
            == f"{self.character} gained experience: +{xp_increase.xp} XP!"
        )
        assert xp_increase.xp == form.cleaned_data["xp"]
        assertRedirects(response, self.game.get_absolute_url())

    def test_creation_ko_invalid_form(self, client):
        xp = random.randint(-20, 0)
        data = {"xp": f"{xp}"}
        form = IncreaseXpForm(data)
        assert form.is_valid() is False
        assert pytest.raises(ValidationError)


@pytest.mark.django_db
class TestDamageView:
    path_name = "damage-create"

    @pytest.fixture(autouse=True)
    def setup(self, client):
        user = User.objects.get(username="master")
        client.force_login(user)
        self.game = Game.objects.last()
        self.character = Character.objects.last()

    @pytest.fixture(autouse=True)
    def tear_down(self):
        yield cache.clear()

    def test_view_mapping(self, client):
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == DamageView

    def test_template_mapping(self, client):
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        assert response.status_code == 200
        assertTemplateUsed(response, "game/damage.html")

    def test_game_not_exists(self, client):
        game_id = random.randint(10000, 99999)
        response = client.get(
            reverse(self.path_name, args=[game_id, self.character.id])
        )
        assert response.status_code == 404
        assert pytest.raises(Http404)

    def test_character_not_exists(self, client):
        character_id = random.randint(10000, 99999)
        response = client.get(
            reverse(self.path_name, args=[self.game.id, character_id])
        )
        assert response.status_code == 404
        assert pytest.raises(Http404)

    def test_context_data(self, client):
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        assert response.status_code == 200
        assert response.context["game"] == self.game
        assert response.context["character"] == self.character

    def test_game_is_under_preparation(self, client):
        self.game.status = "P"
        self.game.save()
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        assert response.status_code == 403
        assert pytest.raises(PermissionDenied)

    def test_creation_ok(self, client):
        hp = random.randint(1, 20)
        data = {"hp": f"{hp}"}
        form = DamageForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            ),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        damage = Damage.objects.last()
        assert damage.game == self.game
        assert damage.character == self.character
        assert damage.date.second - timezone.now().second <= 2
        assert damage.message == f"{self.character} was hit: -{damage.hp} HP!"
        assert damage.hp == form.cleaned_data["hp"]
        assertRedirects(response, self.game.get_absolute_url())

    def test_creation_ko_invalid_form(self, client):
        hp = random.randint(-20, 0)
        data = {"hp": f"{hp}"}
        form = DamageForm(data)
        assert form.is_valid() is False
        assert pytest.raises(ValidationError)

    def test_death(self, client):
        hp = 1000
        data = {"hp": f"{hp}"}
        form = DamageForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            ),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        damage = Damage.objects.last()
        assert damage.game == self.game
        assert damage.character == self.character
        assert damage.date.second - timezone.now().second <= 2
        assert (
            damage.message
            == f"{self.character} was hit: -{damage.hp} HP! {self.character} is dead."
        )
        assert damage.hp == form.cleaned_data["hp"]
        assert hasattr(self.character, "player") is False
        assert self.character.hp == self.character.max_hp
        assertRedirects(response, self.game.get_absolute_url())


@pytest.mark.django_db
class TestHealView:
    path_name = "healing-create"

    @pytest.fixture(autouse=True)
    def setup(self, client):
        user = User.objects.get(username="master")
        client.force_login(user)
        self.game = Game.objects.last()
        self.character = Character.objects.last()
        # The character needs to have low HP, in order to be healed.
        self.character.hp = 1
        self.character.save()

    @pytest.fixture(autouse=True)
    def tear_down(self, client):
        yield cache.clear()

    def test_view_mapping(self, client):
        response = client.get(
            reverse(self.path_name, args=[self.game.id, self.character.id])
        )
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == HealingView

    def test_template_mapping(self, client):
        response = client.get(
            reverse(self.path_name, args=[self.game.id, self.character.id])
        )
        assert response.status_code == 200
        assertTemplateUsed(response, "game/heal.html")

    def test_game_not_exists(self, client):
        game_id = random.randint(10000, 99999)
        response = client.get(
            reverse(self.path_name, args=[game_id, self.character.id])
        )
        assert response.status_code == 404
        assert pytest.raises(Http404)

    def test_character_not_exists(self, client):
        character_id = random.randint(10000, 99999)
        response = client.get(
            reverse(self.path_name, args=[self.game.id, character_id])
        )
        assert response.status_code == 404
        assert pytest.raises(Http404)

    def test_context_data(self, client):
        response = client.get(
            reverse(self.path_name, args=[self.game.id, self.character.id])
        )
        assert response.status_code == 200
        assert response.context["game"] == self.game
        assert response.context["character"] == self.character

    def test_game_is_under_preparation(self, client):
        self.game.status = "P"
        self.game.save()
        response = client.get(
            reverse(self.path_name, args=[self.game.id, self.character.id])
        )
        assert response.status_code == 403
        assert pytest.raises(PermissionDenied)

    def test_creation_ok(self, client):
        hp = random.randint(1, 20)
        data = {"hp": f"{hp}"}
        form = HealForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name, args=[self.game.id, self.character.id]),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        healing = Healing.objects.last()
        assert healing.game == self.game
        assert healing.character == self.character
        assert healing.date.second - timezone.now().second <= 2
        assert healing.message == f"{self.character} was healed: +{healing.hp} HP!"
        assert healing.hp == form.cleaned_data["hp"]
        assertRedirects(response, self.game.get_absolute_url())

    def test_creation_ko_invalid_form(self, client):
        hp = random.randint(-20, 0)
        data = {"hp": f"{hp}"}
        form = HealForm(data)
        assert form.is_valid() is False
        assert pytest.raises(ValidationError)

    def test_healing_not_exceed_character_max_hp(self, client):
        hp = 1000
        data = {"hp": f"{hp}"}
        form = HealForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name, args=[self.game.id, self.character.id]),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        healing = Healing.objects.last()
        assert healing.game == self.game
        assert healing.character == self.character
        assert healing.date.second - timezone.now().second <= 2
        assert healing.message == f"{self.character} was healed: +{healing.hp} HP!"
        assert healing.hp == self.character.max_hp - self.character.hp
        assertRedirects(response, self.game.get_absolute_url())
