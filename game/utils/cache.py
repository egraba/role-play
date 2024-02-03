def game_key(game_id: int) -> str:
    """
    Game cache key.

    Args:
        game_id (int): Game identifier.

    Returns:
        str: Corresponding cache key.
    """
    return f"game_{game_id}"
