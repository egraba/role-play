from django.test import TestCase
from faker import Faker

from game.utils import get_players_emails
from utils.testing.factories import GameFactory, PlayerFactory


class GetPlayersEmailsTest(TestCase):
    def test_all_users_have_email(self):
        fake = Faker()
        game = GameFactory()
        emails = set()
        for _ in range(5):
            email = fake.email()
            emails.add(email)
            PlayerFactory(game=game, character__user__email=email)
        self.assertEqual(get_players_emails(game), list(emails))

    def test_same_emails(self):
        fake = Faker()
        game = GameFactory()
        emails = set()
        email = fake.email()
        emails.add(email)
        for i in range(5):
            PlayerFactory(game=game, character__user__email=email)
        self.assertEqual(get_players_emails(game), list(emails))
