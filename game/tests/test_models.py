import random

from django.db import models
from django.test import TestCase
from django.utils import timezone
from faker import Faker

from game.models import (
    Choice,
    Damage,
    DiceLaunch,
    Event,
    Game,
    Healing,
    Master,
    Player,
    Quest,
    XpIncrease,
)
from utils.testing.factories import (
    EventFactory,
    GameFactory,
    PlayerFactory,
    QuestFactory,
)


class GameModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        GameFactory()

    def setUp(self):
        self.game = Game.objects.last()

    def test_name_type(self):
        name = self.game._meta.get_field("name")
        self.assertTrue(name, models.CharField)

    def test_name_max_length(self):
        max_length = self.game._meta.get_field("name").max_length
        self.assertEqual(max_length, 100)

    def test_campaign_type(self):
        campaign = self.game._meta.get_field("campaign")
        self.assertTrue(campaign, models.ForeignKey)

    def test_start_date_type(self):
        start_date = self.game._meta.get_field("start_date")
        self.assertTrue(start_date, models.DateTimeField)

    def test_status_type(self):
        status = self.game._meta.get_field("status")
        self.assertTrue(status, models.CharField)

    def test_str_is_name(self):
        self.assertEqual(str(self.game), self.game.name)

    def test_status_methods(self):
        # Under preparation
        self.assertTrue(self.game.is_under_preparation())
        self.assertFalse(self.game.is_ongoing())

        # Ongoing
        number_of_players = 5
        for _ in range(number_of_players):
            PlayerFactory(game=self.game)
        self.game.start()
        self.game.save()
        self.assertFalse(self.game.is_under_preparation())
        self.assertTrue(self.game.is_ongoing())


class MasterModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        GameFactory()

    def setUp(self):
        self.master = Master.objects.last()

    def test_user_type(self):
        user = self.master._meta.get_field("user")
        self.assertTrue(user, models.ForeignKey)

    def test_game_type(self):
        game = self.master._meta.get_field("game")
        self.assertTrue(game, models.OneToOneField)

    def test_str(self):
        self.assertEqual(str(self.master), self.master.user.username)


class PlayerModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = GameFactory()
        PlayerFactory(game=game)

    def setUp(self):
        self.player = Player.objects.last()

    def test_character_type(self):
        character = self.player._meta.get_field("character")
        self.assertTrue(character, models.ForeignKey)

    def test_game_type(self):
        game = self.player._meta.get_field("game")
        self.assertTrue(game, models.ForeignKey)

    def test_str(self):
        self.assertEqual(str(self.player), self.player.character.user.username)


class EventModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = GameFactory()
        EventFactory(game=game)

    def setUp(self):
        self.event = Event.objects.last()

    def test_game_type(self):
        game = self.event._meta.get_field("game")
        self.assertTrue(game, models.ForeignKey)

    def test_date_type(self):
        date = self.event._meta.get_field("date")
        self.assertTrue(date, models.DateTimeField)

    def test_date_default_value(self):
        self.assertLessEqual(self.event.date.second - timezone.now().second, 2)

    def test_message_type(self):
        message = self.event._meta.get_field("message")
        self.assertTrue(message, models.CharField)

    def test_message_max_length(self):
        max_length = self.event._meta.get_field("message").max_length
        self.assertEqual(max_length, 100)

    def test_str(self):
        self.assertEqual(str(self.event), self.event.message)


class QuestModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = GameFactory()
        QuestFactory(game=game)

    def setUp(self):
        self.quest = Quest.objects.last()

    def test_content_type(self):
        content = self.quest._meta.get_field("content")
        self.assertTrue(content, models.CharField)

    def test_content_max_length(self):
        max_length = self.quest._meta.get_field("content").max_length
        self.assertEqual(max_length, 1000)

    def test_str(self):
        self.assertEqual(str(self.quest), self.quest.content)


class XpIncreaseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = GameFactory()
        player = PlayerFactory(game=game)
        XpIncrease.objects.create(
            game=game, character=player.character, xp=random.randint(1, 20)
        )

    def setUp(self):
        self.xp_increase = XpIncrease.objects.last()

    def test_hp_type(self):
        xp = self.xp_increase._meta.get_field("xp")
        self.assertTrue(xp, models.SmallIntegerField)

    def test_str(self):
        self.assertEqual(str(self.xp_increase), str(self.xp_increase.xp))


class DamageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = GameFactory()
        player = PlayerFactory(game=game)
        Damage.objects.create(
            game=game, character=player.character, hp=random.randint(1, 20)
        )

    def setUp(self):
        self.damage = Damage.objects.last()

    def test_hp_type(self):
        hp = self.damage._meta.get_field("hp")
        self.assertTrue(hp, models.SmallIntegerField)

    def test_str(self):
        self.assertEqual(str(self.damage), str(self.damage.hp))


class HealingModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = GameFactory()
        player = PlayerFactory(game=game)
        Healing.objects.create(
            game=game, character=player.character, hp=random.randint(1, 20)
        )

    def setUp(self):
        self.healing = Healing.objects.last()

    def test_hp_type(self):
        hp = self.healing._meta.get_field("hp")
        self.assertTrue(hp, models.SmallIntegerField)

    def test_str(self):
        self.assertEqual(str(self.healing), str(self.healing.hp))


class DiceLaunchModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = GameFactory()
        player = PlayerFactory(game=game)
        DiceLaunch.objects.create(
            game=game, character=player.character, score=random.randint(1, 20)
        )

    def setUp(self):
        self.dice_launch = DiceLaunch.objects.last()

    def test_character_type(self):
        character = self.dice_launch._meta.get_field("character")
        self.assertTrue(character, models.ForeignKey)

    def test_score_type(self):
        score = self.dice_launch._meta.get_field("score")
        self.assertTrue(score, models.SmallIntegerField)

    def test_str(self):
        self.assertEqual(str(self.dice_launch), str(self.dice_launch.score))


class ChoiceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = GameFactory()
        player = PlayerFactory(game=game)
        fake = Faker()
        Choice.objects.create(
            game=game,
            character=player.character,
            selection=fake.text(max_nb_chars=50),
        )

    def setUp(self):
        self.choice = Choice.objects.last()

    def test_character_type(self):
        character = self.choice._meta.get_field("character")
        self.assertTrue(character, models.ForeignKey)

    def test_selection_type(self):
        selection = self.choice._meta.get_field("selection")
        self.assertTrue(selection, models.SmallIntegerField)

    def test_selection_max_length(self):
        max_length = self.choice._meta.get_field("selection").max_length
        self.assertEqual(max_length, 50)

    def test_str(self):
        self.assertEqual(str(self.choice), self.choice.selection)
