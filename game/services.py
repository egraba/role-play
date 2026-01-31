import logging
from datetime import datetime

from character.models.character import Character

from .constants.events import RollStatus, RollType
from .models.combat import Combat
from .models.events import (
    CombatInitativeOrderSet,
    CombatInitialization,
    CombatInitiativeRequest,
    CombatInitiativeResponse,
    CombatInitiativeResult,
    CombatStarted,
    DiceRoll,
    Message,
    RollRequest,
    RollResponse,
    RollResult,
    TurnStarted,
)
from .models.game import Actor, Game, Master, Player
from .rolls import perform_combat_initiative_roll, perform_roll
from .utils.channels import send_to_channel
from user.models import User

logger = logging.getLogger(__name__)


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

    @staticmethod
    def process_roll(
        game: Game,
        player: Player,
        date: datetime,
        roll_type: RollType,
    ) -> RollResult:
        """
        Process a dice roll.

        Args:
            game: The game instance
            player: The player performing the roll
            date: The timestamp of the roll
            roll_type: The type of roll (ability check or saving throw)

        Returns:
            The RollResult instance

        Raises:
            RollRequest.DoesNotExist: If no pending roll request found
        """
        logger.info(f"Processing roll: {game.id=}, {player.id=}, {roll_type=}, {date=}")

        # Retrieve the corresponding roll request.
        roll_request = RollRequest.objects.filter(
            roll_type=roll_type, player=player, status=RollStatus.PENDING
        ).first()
        if roll_request is None:
            raise RollRequest.DoesNotExist("Roll request not found")
        logger.info(f"{roll_request=}, {roll_request.player=}")

        # Store the roll response.
        roll_response = RollResponse.objects.create(
            game=game, author=player, date=date, request=roll_request
        )
        logger.info(f"{roll_response.request=}")

        score, result = perform_roll(player, roll_request)
        roll_result = RollResult.objects.create(
            game=game,
            author=player,
            date=date,
            request=roll_request,
            response=roll_response,
            score=score,
            result=result,
        )

        # The corresponding roll request is considered now as done.
        roll_request.status = RollStatus.DONE
        roll_request.save()

        logger.info(
            f"{roll_result.request=}, {roll_result.score=}, {roll_result.result=}"
        )
        send_to_channel(roll_result)

        return roll_result

    @staticmethod
    def process_combat_initiative_roll(
        game: Game,
        player: Player,
        date: datetime,
    ) -> CombatInitiativeResult:
        """
        Process a dice roll for combat initiative.
        After each roll, checks if all fighters have rolled and starts combat if so.

        Args:
            game: The game instance
            player: The player performing the roll
            date: The timestamp of the roll

        Returns:
            The CombatInitiativeResult instance

        Raises:
            CombatInitiativeRequest.DoesNotExist: If no pending initiative request found
        """
        logger.info(f"Processing combat initiative: {game.id=}, {player.id=}, {date=}")

        # Retrieve the corresponding roll request.
        roll_request = CombatInitiativeRequest.objects.filter(
            fighter__player=player, status=RollStatus.PENDING
        ).first()
        if roll_request is None:
            raise CombatInitiativeRequest.DoesNotExist("Roll request not found")
        logger.info(f"{roll_request=}, {roll_request.fighter=}")

        # Store the roll response.
        roll_response = CombatInitiativeResponse.objects.create(
            request=roll_request,
            game=game,
            author=player,
        )
        logger.info(f"{roll_response.request=}")

        score = perform_combat_initiative_roll(roll_request.fighter)
        roll_result = CombatInitiativeResult.objects.create(
            fighter=roll_request.fighter,
            game=game,
            author=player,
            request=roll_request,
            response=roll_response,
            score=score,
        )

        # The corresponding roll request is considered now as done.
        roll_request.status = RollStatus.DONE
        roll_request.save()

        logger.info(f"{roll_result.request=}, {roll_result.score=}")
        send_to_channel(roll_result)

        # Check if all fighters have rolled initiative
        combat = roll_request.fighter.combat
        _check_and_start_combat(combat, game)

        return roll_result


def _check_and_start_combat(combat: Combat, game: Game) -> None:
    """
    Check if all fighters have rolled initiative and start combat if so.
    This replaces the celery-beat periodic task with immediate checking.
    """
    if not combat.all_initiative_rolled():
        logger.info("Still waiting for initiative rolls")
        return

    logger.info("All initiative rolled!")
    logger.info(f"Initiative order={combat.get_initiative_order()}")

    # Get the author from the CombatInitialization event
    combat_init = CombatInitialization.objects.get(combat=combat)

    # Create initiative order set event (only if not already created)
    initiative_order_set, created = CombatInitativeOrderSet.objects.get_or_create(
        combat=combat,
        game=game,
        author=combat_init.author,
    )

    if created:
        send_to_channel(initiative_order_set)

        # Start combat and create turn started event
        first_fighter = combat.start_combat()
        if first_fighter:
            combat_started = CombatStarted.objects.create(
                combat=combat,
                game=game,
                author=combat_init.author,
            )
            send_to_channel(combat_started)

            turn_started = TurnStarted.objects.create(
                combat=combat,
                fighter=first_fighter,
                round_number=combat.current_round,
                game=game,
                author=combat_init.author,
            )
            send_to_channel(turn_started)
            logger.info(f"Combat started! First turn: {first_fighter}")


class DiceRollService:
    """Service for creating dice roll events."""

    @classmethod
    def create_dice_roll(
        cls,
        game: Game,
        user: "User",
        dice_notation: str,
        dice_type: int,
        num_dice: int,
        modifier: int,
        individual_rolls: list[int],
        total: int,
        roll_purpose: str = "",
    ) -> DiceRoll:
        """
        Create a dice roll event, save to DB, and broadcast to channel.

        Args:
            game: The game instance
            user: The authenticated user making the roll
            dice_notation: String like "3d6"
            dice_type: The die type (4, 6, 8, 10, 12, 20)
            num_dice: Number of dice rolled
            modifier: Modifier applied to the roll
            individual_rolls: List of individual die results
            total: Final total including modifier
            roll_purpose: Optional description of what the roll is for

        Returns:
            The created DiceRoll instance
        """
        author = GameEventService.get_author(game, user)
        dice_roll = DiceRoll.objects.create(
            game=game,
            author=author,
            dice_notation=dice_notation,
            dice_type=dice_type,
            num_dice=num_dice,
            modifier=modifier,
            individual_rolls=individual_rolls,
            total=total,
            roll_purpose=roll_purpose,
        )
        send_to_channel(dice_roll)
        return dice_roll
