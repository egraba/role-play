from datetime import datetime

from character.models.character import Character

from .models.events import Message
from .models.game import Actor, Game, Master, Player
from .utils.channels import send_to_channel
from user.models import User


class GameEventService:
    """Encapsulates event creation and broadcasting."""

    @staticmethod
    def get_author(game: Game, user: User) -> Actor:
        """
        Resolve user to Master or Player actor.

        Checks Master first, then Player. This handles the case where
        a user could be both Master and Player in the same game.

        Args:
            game: The game instance
            user: The authenticated user

        Returns:
            The Actor (Master or Player) for this user in the game

        Raises:
            Actor.DoesNotExist: If user is not a participant in the game
        """
        # Check if user is the Master of this game
        try:
            return Master.objects.get(game=game, user=user)
        except Master.DoesNotExist:
            pass

        # Check if user is a Player in this game
        try:
            return Player.objects.get(game=game, user=user)
        except Player.DoesNotExist:
            pass

        raise Actor.DoesNotExist(
            f"User {user} is not a Master or Player in game {game}"
        )

    @classmethod
    def create_message(
        cls, game: Game, user: User, content: str, date: datetime
    ) -> Message:
        """
        Create a message event, save to DB, and broadcast to channel.

        Args:
            game: The game instance
            user: The authenticated user sending the message
            content: The message content
            date: The timestamp of the message

        Returns:
            The created Message instance
        """
        author = cls.get_author(game, user)
        message = Message.objects.create(
            game=game,
            author=author,
            date=date,
            content=content,
        )
        send_to_channel(message)
        return message

    @staticmethod
    def get_character(user: User) -> Character:
        """
        Get the character for a user.

        Args:
            user: The authenticated user

        Returns:
            The Character instance

        Raises:
            Character.DoesNotExist: If user has no character
        """
        return Character.objects.get(user=user)

    @staticmethod
    def get_player(game: Game, user: User) -> Player:
        """
        Get the player for a user in a game.

        Args:
            game: The game instance
            user: The authenticated user

        Returns:
            The Player instance

        Raises:
            Player.DoesNotExist: If user is not a player in the game
        """
        return Player.objects.get(game=game, user=user)
