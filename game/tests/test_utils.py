from django.test import TestCase
from faker import Faker

import game.utils as gutils
import utils.testing.factories as utfactories


class GetPlayersEmailsTest(TestCase):
    def test_all_users_have_email(self):
        fake = Faker()
        game = utfactories.GameFactory()
        emails = set()
        for _ in range(5):
            email = fake.email()
            emails.add(email)
            utfactories.PlayerFactory(game=game, character__user__email=email)
        self.assertEqual(gutils.get_players_emails(game), list(emails))

    def test_same_emails(self):
        fake = Faker()
        game = utfactories.GameFactory()
        emails = set()
        email = fake.email()
        emails.add(email)
        for i in range(5):
            utfactories.PlayerFactory(game=game, character__user__email=email)
        self.assertEqual(gutils.get_players_emails(game), list(emails))
