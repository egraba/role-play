import os

from django.test import TestCase
from email_validator import validate_email
from faker import Faker

import game.utils as gutils
import utils.testing.factories as utfactories


class GetMasterEmailTest(TestCase):
    def test_valid_username_format(self):
        fake = Faker()
        username = fake.first_name().lower()
        email_domain = os.environ["EMAIL_DOMAIN"]
        expected_master_email = f"{username}@{email_domain}"
        master_email = gutils.get_master_email(username)
        self.assertEqual(master_email, expected_master_email)
        self.assertTrue(validate_email(master_email))

    def test_invalid_username_format(self):
        fake = Faker()
        username = fake.first_name().lower() + "/..."  # Add some special characters.
        master_email = gutils.get_master_email(username)
        self.assertIsNone(master_email)


class GetPlayersEmailsTest(TestCase):
    def test_all_users_have_email(self):
        fake = Faker()
        game = utfactories.GameFactory()
        emails = set()
        for _ in range(5):
            email = fake.email()
            emails.add(email)
            utfactories.PlayerFactory(game=game, character__user__email=email)
        self.assertEqual(gutils.get_players_emails(game), emails)

    def test_same_emails(self):
        fake = Faker()
        game = utfactories.GameFactory()
        emails = set()
        email = fake.email()
        emails.add(email)
        for i in range(5):
            utfactories.PlayerFactory(game=game, character__user__email=email)
        self.assertEqual(gutils.get_players_emails(game), emails)
