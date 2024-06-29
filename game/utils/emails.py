from ..models.game import Game, Player


def get_players_emails(game: Game) -> list[str]:
    """
    Get the list of emails of all players from a game.
    """
    players = Player.objects.filter(game=game)
    email_set = {
        player.character.user.email
        for player in players
        if player.character.user is not None and player.character.user.email != ""
    }
    return list(email_set)
