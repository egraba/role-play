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

def create_several_games(n):
    l = list()
    for i in range(n):
        l.append(create_game())
    return l

class IndexViewTests(TestCase):
    def test_no_game(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No games are available...")

    def test_several_games(self):
        game_list = create_several_games(random.randint(1, 100))
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            list(response.context['game_list']),
            game_list,
        )

class GameViewTests(TestCase):
    def test_game_exists(self):
        game = create_game()
        game_id = Game.objects.latest('start_date').pk
        response = self.client.get(reverse('game', args=[game_id]))
        self.assertEqual(response.status_code, 200)
        
    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse('game', args=[game_id]))
        self.assertEqual(response.status_code, 404)