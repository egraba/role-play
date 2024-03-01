from datetime import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.mail import send_mail
from django.utils import timezone

from character.models.character import Character

from .models.events import Event, Roll, RollRequest
from .models.game import Game
from .schemas import GameEventType, PlayerType
from .utils.channels import send_to_channel
from .utils.rolls import perform_roll

logger = get_task_logger(__name__)


@shared_task
def send_email(
    subject: str, message: str, from_email: str, recipient_list: list[str]
) -> int:
    """Send an email."""
    return send_mail(subject, message, from_email, recipient_list)


@shared_task
def store_message(game_id: int, date: datetime, message: str) -> None:
    """
    Store the message received in the channel.

    Args:
        game_id (int): Identifier of the game.
        date (datetime): Date on which the message has been sent.
        message (str): Message content.
    """
    game = Game.objects.get(id=game_id)
    Event.objects.create(
        game=game,
        date=date,
        message=message,
    )


@shared_task
def process_roll(
    game_id: int,
    roll_type: RollRequest.RollType,
    date: datetime,
    character_id: int,
    message: str,
) -> None:
    """
    Process a dice roll.

    Args:
        game_id (int): Identifier of the game.
        roll_type (RollRequest.RollType): Type of the roll.
        date (datetime): Date on which the message has been sent from the player.
        character_id (int): Identifier of the character who did the roll.
        message (str): Message content.
    """
    logger.info(f"{game_id=}, {roll_type=}, {date=}, {character_id=}, {message=}")
    try:
        game = Game.objects.get(id=game_id)
        character = Character.objects.get(id=character_id, player__game=game)
    except ObjectDoesNotExist as exc:
        raise PermissionDenied from exc

    # Retrieve the corresponding request.
    request = RollRequest.objects.filter(
        roll_type=roll_type, character=character, status=RollRequest.Status.PENDING
    ).first()
    if request is None:
        raise PermissionDenied

    # Store the message send when the player has clicked on the sending button.
    Event.objects.create(
        game=game,
        date=date,
        message=message,
    )

    score, result = perform_roll(character, request)
    # Roll's message must be created after Roll() constructor call
    # in order to be able to call get_FOO_display(), to display the
    # result in verbose format.
    roll = Roll(
        game=game,
        date=date,
        character=character,
        request=request,
        result=result,
    )
    roll.message = f"[{character.user}]'s score: {score}, \
        {roll_type} result: {roll.get_result_display()}"
    roll.save()

    # The corresponding request is considered now as done.
    request.status = RollRequest.Status.DONE
    request.save()

    # Send the right message to the channel.
    match roll_type:
        case RollRequest.RollType.ABILITY_CHECK:
            result_type = GameEventType.ABILITY_CHECK_RESULT
        case RollRequest.RollType.SAVING_THROW:
            result_type = GameEventType.SAVING_THROW_RESULT

    send_to_channel(
        game_id=game.id,
        game_event={
            "type": result_type,
            "player_type": PlayerType.MASTER,
            "date": timezone.now().isoformat(),
            "message": roll.message,
        },
    )
