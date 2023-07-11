import os

from django.contrib.auth.models import User
from django.test import TestCase
from email_validator import validate_email

import character.models as cmodels
import game.models as gmodels
import game.utils as gutils
import utils.random as utils


class GetMasterEmailTest(TestCase):
    def test_valid_username_format(self):
        username = utils.generate_random_name(20).lower()
        email_domain = os.environ["EMAIL_DOMAIN"]
        expected_master_email = f"{username}@{email_domain}"
        master_email = gutils.get_master_email(username)
        self.assertEqual(master_email, expected_master_email)
        self.assertTrue(validate_email(master_email))

    def test_invalid_username_format(self):
        username = utils.generate_random_string(20)
        master_email = gutils.get_master_email(username)
        self.assertIsNone(master_email)


class GetPlayersEmailsTest(TestCase):
    def test_all_users_have_email(self):
        game = gmodels.Game.objects.create(name=utils.generate_random_name(30))
        emails = set()
        for i in range(5):
            email = (
                utils.generate_random_name(5)
                + "@"
                + utils.generate_random_name(5)
                + ".com"
            )
            emails.add(email)
            user = User.objects.create(username=f"user{i}", email=email)
            character = cmodels.Character.objects.create(name=f"character{i}")
            gmodels.Player.objects.create(game=game, character=character, user=user)
        self.assertEqual(gutils.get_players_emails(game), emails)

    def test_some_emails_missing(self):
        game = gmodels.Game.objects.create(name=utils.generate_random_name(30))
        emails = set()
        for i in range(5):
            if i % 2 == 0:
                email = (
                    utils.generate_random_name(5)
                    + "@"
                    + utils.generate_random_name(5)
                    + ".com"
                )
                emails.add(email)
                user = User.objects.create(username=f"user{i}", email=email)
                character = cmodels.Character.objects.create(name=f"character{i}")
                gmodels.Player.objects.create(game=game, character=character, user=user)
            else:
                user = User.objects.create(username=f"user{i}")
                character = cmodels.Character.objects.create(name=f"character{i}")
                gmodels.Player.objects.create(game=game, character=character, user=user)
        self.assertEqual(gutils.get_players_emails(game), emails)

    def test_same_emails(self):
        game = gmodels.Game.objects.create(name=utils.generate_random_name(30))
        emails = set()
        email = (
            utils.generate_random_name(5) + "@" + utils.generate_random_name(5) + ".com"
        )
        emails.add(email)
        for i in range(5):
            user = User.objects.create(username=f"user{i}", email=email)
            character = cmodels.Character.objects.create(name=f"character{i}")
            gmodels.Player.objects.create(game=game, character=character, user=user)
        self.assertEqual(gutils.get_players_emails(game), emails)
