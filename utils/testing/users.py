from django.contrib.auth.models import User

import utils.testing.random as utrandom


def create_user():
    user = User.objects.create(username=utrandom.ascii_letters_string(5))
    user.set_password("pwd")
    user.save()
