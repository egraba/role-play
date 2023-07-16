from django.contrib.auth.models import User

import utils.testing.random as utrandom


def create_user(username="", password=""):
    if username == "":
        username = utrandom.ascii_letters_string(5)
    if password == "":
        password = "pwd"
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()
    return user
