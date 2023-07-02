import os

import game.models as gmodels


def get_master_email(username):
    email_domain = os.environ["EMAIL_DOMAIN"]
    email = f"{username}@{email_domain}"
    return email


def get_players_emails(game):
    players = gmodels.Character.objects.filter(game=game)
    return [player.user.email for player in players if player.user is not None]
