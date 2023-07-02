import os

from django.test import TestCase
from email_validator import validate_email

import game.utils as gutils
from game.tests import utils


class GetMasterEmailTest(TestCase):
    def test_valid_username(self):
        username = utils.generate_random_name(20)
        email_domain = os.environ["EMAIL_DOMAIN"]
        expected_master_email = f"{username}@{email_domain}"
        master_email = gutils.get_master_email(username)
        self.assertEqual(master_email, expected_master_email)
        self.assertTrue(validate_email(master_email))
