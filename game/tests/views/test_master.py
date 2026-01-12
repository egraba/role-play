import random

import pytest
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from freezegun import freeze_time
from pytest_django.asserts import (
    assertQuerySetEqual,
    assertRedirects,
    assertTemplateUsed,
)

from character.constants.abilities import AbilityName
from character.models.character import Character
from character.tests.factories import CharacterFactory
from game.constants.combat import FighterAttributeChoices
from game.constants.events import DifficultyClass, RollType
from game.exceptions import UserHasNoCharacter
from game.flows import GameFlow
from game.forms import CombatCreateForm, QuestCreateForm
from game.models.combat import Combat
from game.models.events import Event, Quest, RollRequest, UserInvitation
from game.models.game import Game, Player
from game.constants.combat import CombatState
from game.models.events import (
    CombatEnded,
    CombatInitialization,
    RoundEnded,
    TurnEnded,
    TurnStarted,
)
from game.views.master import (
    AbilityCheckRequestView,
    CombatAdvanceTurnView,
    CombatCreateView,
    CombatEndView,
    GameStartView,
    QuestCreateView,
    UserInviteConfirmView,
    UserInviteView,
)
from user.models import User
from user.tests.factories import UserFactory
from utils.constants import FREEZED_TIME

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


class TestUserInviteView:
    path_name = "game-invite-user"

    @pytest.fixture
    def game(self, client):
        user = UserFactory(username="master")
        client.force_login(user)
        return GameFactory(master__user__username="master")

    def test_view_mapping(self, client, game):
        response = client.get(reverse(self.path_name, args=(game.id,)))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == UserInviteView

    def test_template_mapping(self, client, game):
        response = client.get(reverse(self.path_name, args=(game.id,)))
        assert response.status_code == 200
        assertTemplateUsed(response, "game/user_invite.html")

    def test_pagination_size(self, client, game, create_characters):
        response = client.get(reverse(self.path_name, args=(game.id,)))
        assert response.status_code == 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["user_list"]) == 10

    def test_pagination_size_next_page(self, client, game, create_characters):
        response = client.get(reverse(self.path_name, args=(game.id,)) + "?page=2")
        assert response.status_code, 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["user_list"]) == 2

    def test_ordering(self, client, game, create_characters):
        response = client.get(reverse(self.path_name, args=(game.id,)))
        assert response.status_code == 200
        user_list = [user.username for user in response.context["user_list"]]
        assert user_list == sorted(user_list)

    def test_game_not_exists(self, client, game):
        game_id = random.randint(10000, 99999)
        response = client.get(reverse(self.path_name, args=(game_id,)))
        assert response.status_code == 404
        assert pytest.raises(Http404)

    def test_context_data(self, client, game, create_characters):
        user_list = User.objects.filter(character__isnull=False, player__isnull=True)
        response = client.get(reverse(self.path_name, args=(game.id,)))
        assert set(response.context["user_list"]).issubset(user_list)

    def test_context_data_all_characters_already_assigned(self, client, game):
        Character.objects.filter(player=None).delete()
        response = client.get(reverse(self.path_name, args=(game.id,)))
        assertQuerySetEqual(response.context["user_list"], [])


@pytest.fixture(scope="class")
def create_player(django_db_blocker):
    with django_db_blocker.unblock():
        game = GameFactory(master__user__username="master")
        PlayerFactory(game=game)


class TestUserInviteConfirmView:
    path_name = "game-invite-user-confirm"

    @pytest.fixture
    def game(self, client, create_player):
        user = User.objects.get(username="master")
        client.force_login(user)
        return GameFactory(master__user__username="master")

    @pytest.fixture
    def user(self):
        # Users must have characters when accessing this view.
        character = CharacterFactory()
        return character.user

    @pytest.fixture
    def user_without_character(self):
        return UserFactory()

    def test_view_mapping(self, client, game, user):
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    game.id,
                    user.id,
                ),
            )
        )
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == UserInviteConfirmView

    def test_template_mapping(self, client, game, user):
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    game.id,
                    user.id,
                ),
            )
        )
        assert response.status_code == 200
        assertTemplateUsed(response, "game/user_invite_confirm.html")

    def test_game_not_exists(self, client, game, user):
        game_id = random.randint(10000, 99999)
        response = client.get(
            reverse(
                self.path_name,
                args=(
                    game_id,
                    user.id,
                ),
            )
        )
        assert response.status_code == 404
        assert pytest.raises(Http404)

    @freeze_time(FREEZED_TIME)
    def test_user_with_character_added_to_game(self, client, game, user):
        response = client.post(
            reverse(
                self.path_name,
                args=(
                    game.id,
                    user.id,
                ),
            )
        )
        assert response.status_code == 302
        assertRedirects(response, reverse("game", args=(game.id,)))
        assert user.player.game == game
        user_invitation = UserInvitation.objects.last()
        assert user_invitation.date == timezone.now()
        assert user_invitation.game == game
        assert user_invitation.user == user

    @freeze_time(FREEZED_TIME)
    def test_user_without_character_raises_exception(
        self, client, game, user_without_character
    ):
        with pytest.raises(UserHasNoCharacter):
            client.post(
                reverse(
                    self.path_name,
                    args=(
                        game.id,
                        user_without_character.id,
                    ),
                )
            )


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

    @freeze_time(FREEZED_TIME)
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
        assert game.start_date == timezone.now()
        event = Event.objects.last()
        assert event.date == timezone.now()
        assert event.game == game

    def test_game_start_not_enough_characters(self, client, game):
        PlayerFactory(game=game)
        response = client.post(reverse(self.path_name, args=(game.id,)))
        assert response.status_code == 302
        assert pytest.raises(PermissionDenied)
        flow = GameFlow(game)
        assert flow.is_under_preparation()
        assertRedirects(response, reverse("game-start-error", args=(game.id,)))


@pytest.fixture
def started_game(db):
    """Create a started game with players.

    Note: This fixture is function-scoped to avoid race conditions
    with parallel test execution (pytest-xdist).
    """
    game = GameFactory()
    number_of_players = 3
    for _ in range(number_of_players):
        PlayerFactory(game=game)
    flow = GameFlow(game)
    flow.start()
    return game


class TestQuestCreateView:
    path_name = "quest-create"

    @pytest.fixture
    def login(self, client, started_game):
        user = started_game.master.user
        client.force_login(user)

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

    def test_quest_creation(self, client, login, started_game, monkeypatch):
        def patched_enrich_quest(self, prompt: str) -> str:
            return "some enriched quest"

        monkeypatch.setattr(
            "ai.generators.TextGenerator.enrich_quest", patched_enrich_quest
        )
        fake = Faker()
        environment = fake.text(100)
        data = {"environment": f"{environment}"}
        form = QuestCreateForm(data)
        assert form.is_valid()
        response = client.post(
            reverse(self.path_name, args=(started_game.id,)), data=form.cleaned_data
        )
        assert response.status_code == 302
        quest = Quest.objects.filter(game=started_game).last()
        assert quest.game == started_game
        assert quest.environment == "some enriched quest"
        assertRedirects(response, started_game.get_absolute_url())


class TestCombatCreateView:
    path_name = "combat-create"

    @pytest.fixture(autouse=True)
    def login(self, client, started_game):
        user = started_game.master.user
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
        # Each combat creates new fighters, verify the fighters belong to this combat
        fighters = list(combat.fighter_set.all())
        fighter_characters = [f.character for f in fighters]
        assert characters.first() in fighter_characters
        assert characters.last() in fighter_characters


class TestAbilityCheckRequestView:
    path_name = "ability-check-request-create"

    @pytest.fixture
    def game_with_master(self):
        game = GameFactory()
        PlayerFactory(game=game)
        PlayerFactory(game=game)
        flow = GameFlow(game)
        flow.start()
        return game

    @pytest.fixture
    def logged_in_client(self, client, game_with_master):
        user = game_with_master.master.user
        client.force_login(user)
        return client

    def test_view_mapping(self, logged_in_client, game_with_master):
        response = logged_in_client.get(
            reverse(self.path_name, args=(game_with_master.id,))
        )
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == AbilityCheckRequestView

    def test_template_mapping(self, logged_in_client, game_with_master):
        response = logged_in_client.get(
            reverse(self.path_name, args=(game_with_master.id,))
        )
        assert response.status_code == 200
        assertTemplateUsed(response, "game/ability_check_request.html")

    def test_game_not_exists(self, logged_in_client):
        game_id = random.randint(10000, 99999)
        response = logged_in_client.get(reverse(self.path_name, args=(game_id,)))
        assert response.status_code == 404
        assert pytest.raises(Http404)

    def test_form_valid_creates_roll_request_with_author(
        self, logged_in_client, game_with_master
    ):
        player = Player.objects.filter(game=game_with_master).first()
        data = {
            "player": player.id,
            "ability_type": AbilityName.STRENGTH,
            "difficulty_class": DifficultyClass.EASY,
        }
        response = logged_in_client.post(
            reverse(self.path_name, args=(game_with_master.id,)), data=data
        )
        assert response.status_code == 302
        assertRedirects(response, game_with_master.get_absolute_url())
        roll_request = RollRequest.objects.filter(game=game_with_master).last()
        assert roll_request is not None
        assert roll_request.player == player
        assert roll_request.ability_type == AbilityName.STRENGTH
        assert roll_request.roll_type == RollType.ABILITY_CHECK
        assert roll_request.author is not None
        assert roll_request.author.user == game_with_master.master.user


class TestCombatAdvanceTurnView:
    path_name = "combat-advance-turn"

    @pytest.fixture
    def active_combat(self, started_game):
        """Create a combat that has started with initiative rolled."""
        combat = Combat.objects.create(game=started_game)
        players = list(Player.objects.filter(game=started_game))
        from game.models.combat import Fighter

        # Create fighters with initiative already rolled
        for i, player in enumerate(players[:2]):
            Fighter.objects.create(
                player=player,
                character=player.character,
                combat=combat,
                dexterity_check=15 - i,  # First fighter has higher initiative
            )

        # Create the CombatInitialization event (required by the system)
        CombatInitialization.objects.create(
            game=started_game,
            author=started_game.master.actor_ptr,
            combat=combat,
        )

        # Start the combat
        combat.start_combat()
        return combat

    @pytest.fixture
    def logged_in_master(self, client, started_game):
        user = started_game.master.user
        client.force_login(user)
        return client

    def test_view_mapping(self, logged_in_master, started_game, active_combat):
        response = logged_in_master.post(
            reverse(self.path_name, args=(started_game.id, active_combat.id))
        )
        assert response.status_code == 302
        assert response.resolver_match.func.view_class == CombatAdvanceTurnView

    def test_advance_turn_creates_turn_ended_event(
        self, logged_in_master, started_game, active_combat
    ):
        first_fighter = active_combat.current_fighter
        first_round = active_combat.current_round

        response = logged_in_master.post(
            reverse(self.path_name, args=(started_game.id, active_combat.id))
        )

        assert response.status_code == 302
        assertRedirects(response, started_game.get_absolute_url())

        # Check TurnEnded event was created
        turn_ended = TurnEnded.objects.filter(
            combat=active_combat, fighter=first_fighter
        ).last()
        assert turn_ended is not None
        assert turn_ended.round_number == first_round
        assert turn_ended.game == started_game

    def test_advance_turn_creates_turn_started_event(
        self, logged_in_master, started_game, active_combat
    ):
        first_fighter = active_combat.current_fighter

        logged_in_master.post(
            reverse(self.path_name, args=(started_game.id, active_combat.id))
        )

        active_combat.refresh_from_db()

        # Check TurnStarted event was created for next fighter
        turn_started = TurnStarted.objects.filter(combat=active_combat).last()
        assert turn_started is not None
        assert turn_started.fighter != first_fighter
        assert turn_started.game == started_game

    def test_advance_turn_updates_combat_state(
        self, logged_in_master, started_game, active_combat
    ):
        first_fighter = active_combat.current_fighter

        logged_in_master.post(
            reverse(self.path_name, args=(started_game.id, active_combat.id))
        )

        active_combat.refresh_from_db()
        assert active_combat.current_fighter != first_fighter
        assert active_combat.current_turn_index == 1

    def test_advance_turn_new_round(
        self, logged_in_master, started_game, active_combat
    ):
        """Test that advancing past all fighters creates a new round."""
        num_fighters = active_combat.fighter_set.count()

        # Advance through all fighters
        for _ in range(num_fighters):
            logged_in_master.post(
                reverse(self.path_name, args=(started_game.id, active_combat.id))
            )

        active_combat.refresh_from_db()
        assert active_combat.current_round == 2
        assert active_combat.current_turn_index == 0

        # Check RoundEnded event was created
        round_ended = RoundEnded.objects.filter(combat=active_combat).last()
        assert round_ended is not None
        assert round_ended.round_number == 1

    def test_advance_turn_combat_not_active(
        self, logged_in_master, started_game, active_combat
    ):
        """Test that advancing turn on non-active combat redirects without changes."""
        active_combat.state = CombatState.ENDED
        active_combat.save()

        response = logged_in_master.post(
            reverse(self.path_name, args=(started_game.id, active_combat.id))
        )

        assert response.status_code == 302
        # No new events should be created
        assert TurnEnded.objects.filter(combat=active_combat).count() == 0


class TestCombatEndView:
    path_name = "combat-end"

    @pytest.fixture
    def active_combat(self, started_game):
        """Create a combat that has started with initiative rolled."""
        combat = Combat.objects.create(game=started_game)
        players = list(Player.objects.filter(game=started_game))
        from game.models.combat import Fighter

        # Create fighters with initiative already rolled
        for i, player in enumerate(players[:2]):
            Fighter.objects.create(
                player=player,
                character=player.character,
                combat=combat,
                dexterity_check=15 - i,
            )

        # Create the CombatInitialization event
        CombatInitialization.objects.create(
            game=started_game,
            author=started_game.master.actor_ptr,
            combat=combat,
        )

        # Start the combat
        combat.start_combat()
        return combat

    @pytest.fixture
    def logged_in_master(self, client, started_game):
        user = started_game.master.user
        client.force_login(user)
        return client

    def test_view_mapping(self, logged_in_master, started_game, active_combat):
        response = logged_in_master.post(
            reverse(self.path_name, args=(started_game.id, active_combat.id))
        )
        assert response.status_code == 302
        assert response.resolver_match.func.view_class == CombatEndView

    def test_end_combat_creates_event(
        self, logged_in_master, started_game, active_combat
    ):
        response = logged_in_master.post(
            reverse(self.path_name, args=(started_game.id, active_combat.id))
        )

        assert response.status_code == 302
        assertRedirects(response, started_game.get_absolute_url())

        # Check CombatEnded event was created
        combat_ended = CombatEnded.objects.filter(combat=active_combat).last()
        assert combat_ended is not None
        assert combat_ended.game == started_game

    def test_end_combat_updates_state(
        self, logged_in_master, started_game, active_combat
    ):
        logged_in_master.post(
            reverse(self.path_name, args=(started_game.id, active_combat.id))
        )

        active_combat.refresh_from_db()
        assert active_combat.state == CombatState.ENDED
        assert active_combat.current_fighter is None

    def test_end_combat_already_ended(
        self, logged_in_master, started_game, active_combat
    ):
        """Test that ending an already ended combat redirects without new events."""
        active_combat.state = CombatState.ENDED
        active_combat.save()

        response = logged_in_master.post(
            reverse(self.path_name, args=(started_game.id, active_combat.id))
        )

        assert response.status_code == 302
        # No new CombatEnded event should be created
        assert CombatEnded.objects.filter(combat=active_combat).count() == 0
