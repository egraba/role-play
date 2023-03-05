import random
from datetime import datetime

from django.http import Http404
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from game.forms import CreateGameForm
from game.models import Character, Choice, DiceLaunch, Event, Game, PendingAction, Tale
from game.tests import utils
from game.views import (
    AddCharacterView,
    ChoiceSuccessView,
    ChoiceView,
    CreateGameView,
    DiceLaunchSuccessView,
    DiceLaunchView,
    GameView,
    IndexView,
    StartGameView,
)


def create_character(game):
    return Character.objects.create(
        name=utils.generate_random_name(100),
        game=game,
        race=random.choice(Character.RACES)[0],
    )


def create_several_characters(game):
    character_list = list()
    n = random.randint(2, 10)
    for i in range(n):
        character_list.append(create_character(game))
    return character_list


def create_tale(game):
    return Tale.objects.create(
        date=datetime.now(tz=timezone.utc),
        game=game,
        message=utils.generate_random_string(100),
        description=utils.generate_random_string(500),
    )


def create_several_tales(game):
    tale_list = list()
    n = random.randint(1, 2)
    for i in range(n):
        tale_list.append(create_tale(game))
    return tale_list


def create_pending_action(game, character):
    return PendingAction.objects.create(
        game=game,
        character=character,
        action_type=random.choice(PendingAction.ACTION_TYPES)[0],
    )


class IndexViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_games = 12
        for i in range(number_of_games):
            Game.objects.create(
                name=utils.generate_random_string(20),
                start_date=datetime.now(tz=timezone.utc),
            )

    def test_view_mapping(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, IndexView)

    def test_template_mapping(self):
        response = self.client.get(reverse("index"))
        self.assertTemplateUsed(response, "game/index.html")

    def test_pagination_size(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["game_list"]), 10)

    def test_pagination_size_next_page(self):
        response = self.client.get(reverse("index") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["game_list"]), 2)

    def test_ordering(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        last_date = 0
        for game in response.context["game_list"]:
            if last_date == 0:
                last_date = game.start_date
            else:
                self.assertTrue(last_date >= game.start_date)
                last_date = game.start_date


class CreateGameViewTest(TestCase):
    def test_view_mapping(self):
        response = self.client.get(reverse("game-create"))
        self.assertEqual(response.resolver_match.func.view_class, CreateGameView)

    def test_template_mapping(self):
        response = self.client.get(reverse("game-create"))
        self.assertTemplateUsed(response, "game/creategame.html")

    def test_form_valid(self):
        name = utils.generate_random_name(20)
        description = utils.generate_random_string(100)
        data = {"name": f"{name}", "description": f"{description}"}
        form = CreateGameForm(data)
        self.assertTrue(form.is_valid())
        response = self.client.post(reverse("game-create"), data=form.cleaned_data)
        game = Game.objects.last()
        self.assertEqual(game.name, name)
        tale = Tale.objects.last()
        self.assertEqual(tale.game, game)
        self.assertEqual(tale.message, "The Master created the story.")
        self.assertEqual(tale.description, description)
        self.assertRedirects(response, reverse("index"))


class GameViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Game.objects.create(name=utils.generate_random_string(20))
        game = Game.objects.last()
        number_of_events = 22
        for i in range(number_of_events):
            Event.objects.create(
                game=game,
                message=utils.generate_random_string(100),
            )
        number_of_tales = 3
        for i in range(number_of_tales):
            Tale.objects.create(
                game=game,
                description=utils.generate_random_string(500),
            )

    def test_view_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.resolver_match.func.view_class, GameView)

    def test_template_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertTemplateUsed(response, "game/game.html")

    def test_pagination_size(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["event_list"]), 20)

    def test_pagination_size_next_page(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]) + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["event_list"]), 5)

    def test_ordering(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        last_date = 0
        for game in response.context["game_list"]:
            if last_date == 0:
                last_date = game.start_date
            else:
                self.assertTrue(last_date >= game.start_date)
                last_date = game.start_date

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse("game", args=[game_id]))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_game_last_tale(self):
        game = Game.objects.last()
        tale = Tale.objects.create(game=game)
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tale"], tale)

    def test_context_data(self):
        game1 = Game.objects.create()
        tale1 = Tale.objects.create(game=game1, message="tale1")
        character_list1 = list()
        character_list1.append(Character.objects.create(game=game1, name="A"))
        pending_action_list1 = list()
        pending_action_list1.append(
            PendingAction.objects.create(
                game=game1, character=character_list1[0], message="pending_action1"
            )
        )
        event_list1 = list()
        event_list1.append(Event.objects.filter(message="tale1").last())
        event_list1.append(Event.objects.filter(message="pending_action1").last())
        event_list1.append(Event.objects.create(game=game1, message="event1"))

        game2 = Game.objects.create()
        tale2 = Tale.objects.create(game=game2, message="tale2")
        character_list2 = list()
        character_list2.append(Character.objects.create(game=game2, name="B"))
        pending_action_list2 = list()
        pending_action_list2.append(
            PendingAction.objects.create(
                game=game2, character=character_list2[0], message="pending_action2"
            )
        )
        event_list2 = list()
        event_list2.append(Event.objects.filter(message="tale2").last())
        event_list2.append(Event.objects.filter(message="pending_action2").last())
        event_list2.append(Event.objects.create(game=game2, message="event2"))

        """
        We test that game1 contains the context game1 only.
        """
        response = self.client.get(reverse("game", args=[game1.id]))
        self.assertEqual(response.context["tale"], tale1)
        self.assertQuerysetEqual(set(response.context["event_list"]), set(event_list1))
        self.assertQuerysetEqual(
            list(response.context["character_list"]), character_list1
        )
        self.assertQuerysetEqual(
            list(response.context["pending_action_list"]), pending_action_list1
        )

        """
        We test that game2 contains the context game2 only.
        """
        response = self.client.get(reverse("game", args=[game2.id]))
        self.assertEqual(response.context["tale"], tale2)
        self.assertQuerysetEqual(set(response.context["event_list"]), set(event_list2))
        self.assertQuerysetEqual(
            list(response.context["character_list"]), character_list2
        )
        self.assertQuerysetEqual(
            list(response.context["pending_action_list"]), pending_action_list2
        )


class AddCharacterViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        number_of_characters_with_game = 5
        number_of_characters_without_game = 12
        for i in range(number_of_characters_with_game):
            Character.objects.create(
                name=utils.generate_random_name(10),
                game=game,
                race=random.choice(Character.RACES)[0],
            )
        for i in range(number_of_characters_without_game):
            Character.objects.create(
                name=utils.generate_random_name(10),
                race=random.choice(Character.RACES)[0],
            )

    def test_view_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("add_character", args=[game.id]))
        self.assertEqual(response.resolver_match.func.view_class, AddCharacterView)

    def test_template_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("add_character", args=[game.id]))
        self.assertTemplateUsed(response, "game/addcharacter.html")

    def test_pagination_size(self):
        game = Game.objects.last()
        response = self.client.get(reverse("add_character", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["character_list"]), 10)

    def test_pagination_size_next_page(self):
        game = Game.objects.last()
        response = self.client.get(reverse("add_character", args=[game.id]) + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["character_list"]), 2)

    def test_ordering(self):
        game = Game.objects.last()
        response = self.client.get(reverse("add_character", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        last_xp = 0
        for character in response.context["character_list"]:
            if last_xp == 0:
                last_xp = character.xp
            else:
                self.assertTrue(last_xp >= character.xp)
                last_xp = character.xp

    def test_game_exists(self):
        game = Game.objects.last()
        response = self.client.get(reverse("add_character", args=[game.id]))
        self.assertEqual(response.status_code, 200)

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse("add_character", args=[game_id]))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)


class StartGameViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Game.objects.create()

    def test_view_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-start", args=[game.id]))
        self.assertEqual(response.resolver_match.func.view_class, StartGameView)

    def test_template_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-start", args=[game.id]))
        self.assertTemplateUsed(response, "game/startgame.html")


class DiceLaunchViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        Character.objects.create(
            name=utils.generate_random_name(100),
            game=game,
            race=random.choice(Character.RACES)[0],
        )

    def test_view_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(reverse("launch_dice", args=[game.id, character.id]))
        self.assertEqual(response.resolver_match.func.view_class, DiceLaunchView)

    def test_template_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(reverse("launch_dice", args=[game.id, character.id]))
        self.assertTemplateUsed(response, "game/dice.html")

    def test_view_content(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(reverse("launch_dice", args=[game.id, character.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], game)
        self.assertEqual(response.context["character"], character)
        self.assertContains(response, "! It is your turn.")


class ChoiceViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        Character.objects.create(
            name=utils.generate_random_name(100),
            game=game,
            race=random.choice(Character.RACES)[0],
        )

    def test_view_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(reverse("make_choice", args=[game.id, character.id]))
        self.assertEqual(response.resolver_match.func.view_class, ChoiceView)

    def test_template_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(reverse("make_choice", args=[game.id, character.id]))
        self.assertTemplateUsed(response, "game/choice.html")

    def test_view_content(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(reverse("make_choice", args=[game.id, character.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], game)
        self.assertEqual(response.context["character"], character)


class DiceLaunchSuccessViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        character = Character.objects.create(
            name=utils.generate_random_name(100),
            game=game,
            race=random.choice(Character.RACES)[0],
        )
        DiceLaunch.objects.create(
            game=game, character=character, score=random.randint(1, 20)
        )

    def test_view_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        dice_launch = DiceLaunch.objects.last()
        response = self.client.get(
            reverse(
                "dice_success",
                args=[game.id, character.id, dice_launch.id],
            )
        )
        self.assertEqual(response.resolver_match.func.view_class, DiceLaunchSuccessView)

    def test_template_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        dice_launch = DiceLaunch.objects.last()
        response = self.client.get(
            reverse("dice_success", args=[game.id, character.id, dice_launch.id])
        )
        self.assertTemplateUsed(response, "game/success.html")

    def test_view_content(self):
        game = Game.objects.last()
        character = Character.objects.last()
        dice_launch = DiceLaunch.objects.last()
        response = self.client.get(
            reverse(
                "dice_success",
                args=[game.id, character.id, dice_launch.id],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], game)
        self.assertEqual(response.context["character"], character)
        self.assertEqual(response.context["dice_launch"], dice_launch)
        self.assertContains(
            response, f"{character.name}, your score is: {dice_launch.score}!"
        )


class ChoiceSuccessViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        character = Character.objects.create(
            name=utils.generate_random_name(100),
            game=game,
            race=random.choice(Character.RACES)[0],
        )
        Choice.objects.create(
            game=game,
            character=character,
            selection=utils.generate_random_name(255),
        )

    def test_view_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        choice = Choice.objects.last()
        response = self.client.get(
            reverse("choice_success", args=[game.id, character.id, choice.id])
        )
        self.assertEqual(response.resolver_match.func.view_class, ChoiceSuccessView)

    def test_template_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        choice = Choice.objects.last()
        response = self.client.get(
            reverse("choice_success", args=[game.id, character.id, choice.id])
        )
        self.assertTemplateUsed(response, "game/success.html")

    def test_view_content(self):
        game = Game.objects.last()
        character = Character.objects.last()
        choice = Choice.objects.last()
        response = self.client.get(
            reverse("choice_success", args=[game.id, character.id, choice.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], game)
        self.assertEqual(response.context["character"], character)
        self.assertEqual(response.context["choice"], choice)
        self.assertContains(response, f"{choice.selection}")
