from ..models.game import Game, Player


def get_players_emails(game: Game) -> list[str]:
    """
    Get players emails.

    Args:
        game (Game): Current game.

    Returns:
        list: email list.
    """
    players = Player.objects.filter(game=game)
    email_set = {
        player.character.user.email
        for player in players
        if player.character.user is not None and player.character.user.email != ""
    }
    return list(email_set)
