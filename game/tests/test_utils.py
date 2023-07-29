import os

from django.test import TestCase
from email_validator import validate_email

import game.utils as gutils
import utils.testing.factories as utfactories
import utils.testing.random as utrandom


class GetMasterEmailTest(TestCase):
    def test_valid_username_format(self):
        username = utrandom.ascii_letters_string(20).lower()
        email_domain = os.environ["EMAIL_DOMAIN"]
        expected_master_email = f"{username}@{email_domain}"
        master_email = gutils.get_master_email(username)
        self.assertEqual(master_email, expected_master_email)
        self.assertTrue(validate_email(master_email))

    def test_invalid_username_format(self):
        username = utrandom.printable_string(20)
        master_email = gutils.get_master_email(username)
        self.assertIsNone(master_email)


class GetPlayersEmailsTest(TestCase):
    def test_all_users_have_email(self):
        game = utfactories.GameFactory()
        emails = set()
        for _ in range(5):
            email = (
                utrandom.ascii_letters_string(5)
                + "@"
                + utrandom.ascii_letters_string(5)
                + ".com"
            )
            emails.add(email)
            utfactories.PlayerFactory(game=game, character__user__email=email)
        self.assertEqual(gutils.get_players_emails(game), emails)

    def test_some_emails_missing(self):
        game = utfactories.GameFactory()
        emails = set()
        for i in range(5):
            if i % 2 == 0:
                email = (
                    utrandom.ascii_letters_string(5)
                    + "@"
                    + utrandom.ascii_letters_string(5)
                    + ".com"
                )
                emails.add(email)
                utfactories.PlayerFactory(game=game, character__user__email=email)
            else:
                utfactories.PlayerFactory(game=game)
        self.assertEqual(gutils.get_players_emails(game), emails)

    def test_same_emails(self):
        game = utfactories.GameFactory()
        emails = set()
        email = (
            utrandom.ascii_letters_string(5)
            + "@"
            + utrandom.ascii_letters_string(5)
            + ".com"
        )
        emails.add(email)
        for i in range(5):
            utfactories.PlayerFactory(game=game, character__user__email=email)
        self.assertEqual(gutils.get_players_emails(game), emails)
