import os

from email_validator import EmailNotValidError, validate_email

import game.models as gmodels


def get_master_email(username):
    email_domain = os.environ["EMAIL_DOMAIN"]
    username = username.lower()
    email = f"{username}@{email_domain}"
    try:
        validate_email(email)
    except EmailNotValidError:
        email = None
    return email


def get_players_emails(game):
    players = gmodels.Player.objects.filter(game=game)
    return {
        player.character.user.email
        for player in players
        if player.character.user is not None and player.character.user.email != ""
    }
