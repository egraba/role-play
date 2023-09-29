import game.models as gmodels


def get_players_emails(game):
    players = gmodels.Player.objects.filter(game=game)
    email_set = {
        player.character.user.email
        for player in players
        if player.character.user is not None and player.character.user.email != ""
    }
    return list(email_set)
