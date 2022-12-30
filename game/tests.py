from django.test import TestCase
from django.urls import reverse

from .models import Game

import random
import string

def generate_random_string(length):
    return ''.join(random.choice(string.printable) for i in range(length))

def create_game():
    game_name = generate_random_string(random.randint(1, 255))
    return Game.objects.create(name=game_name)

class IndexViewTests(TestCase):
    def test_no_game(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No games are available...")

    def test_several_games(self):
        game1 = create_game()
        game2 = create_game()
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            list(response.context['game_list']),
            [game1, game2],
        )