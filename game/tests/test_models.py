from django.db import models
from django.test import TestCase
from django.utils import timezone

from game.models import Game
from game.tests import utils


class GameModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Game.objects.create(name=utils.generate_random_string(100))

    def test_start_date_type(self):
        game = Game.objects.get(id=1)
        start_date = game._meta.get_field("start_date")
        self.assertTrue(start_date, models.DateTimeField)

    def test_start_date_default_value(self):
        game = Game.objects.get(id=1)
        self.assertEqual(game.start_date.second, timezone.now().second)

    def test_name_type(self):
        game = Game.objects.get(id=1)
        name = game._meta.get_field("name")
        self.assertTrue(name, models.CharField)

    def test_name_max_length(self):
        game = Game.objects.get(id=1)
        max_length = game._meta.get_field("name").max_length
        self.assertEqual(max_length, 255)

    def test_end_date_type(self):
        game = Game.objects.get(id=1)
        end_date = game._meta.get_field("end_date")
        self.assertTrue(end_date, models.DateTimeField)

    def test_end_date_default_value(self):
        game = Game.objects.get(id=1)
        self.assertEqual(game.end_date, None)

    def test_str_is_name(self):
        game = Game.objects.get(id=1)
        self.assertEqual(str(game), game.name)
