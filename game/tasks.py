from datetime import datetime

from celery import shared_task
from celery.exceptions import InvalidTaskError
from celery.utils.log import get_task_logger
from django.core.cache import cache
from django.core.mail import send_mail as django_send_mail

from character.models.character import Character

from .constants.events import RollStatus, RollType
from .models.combat import Combat
from .models.events import (
    CombatInitiativeRequest,
    CombatInitiativeResponse,
    CombatInitiativeResult,
    Message,
    RollRequest,
    RollResponse,
    RollResult,
)
from .models.game import Game, Player
from .rolls import perform_roll
from .utils.cache import game_key
from .utils.channels import send_to_channel

logger = get_task_logger(__name__)


@shared_task
def send_mail(
    subject: str, message: str, from_email: str, recipient_list: list[str]
) -> int:
    logger.info(f"{subject=}, {message=}, {from_email=}, {recipient_list=}")
    return django_send_mail(subject, message, from_email, recipient_list)


@shared_task
def store_message(
    game_id: int,
    date: datetime,
    message: str,
    is_from_master: bool,
    author_name: str | None = None,
) -> None:
    """
    Store the message received in the channel.
    """
    logger.info(f"{game_id=}, {date=}, {message=}")
    try:
        game = cache.get_or_set(game_key(game_id), Game.objects.get(id=game_id))
    except Game.DoesNotExist as exc:
        raise InvalidTaskError(f"Game [{game_id}] not found") from exc
    if author_name is None:
        author = None
    else:
        try:
            author = Player.objects.get(character__user__username=author_name)
        except Player.DoesNotExist as exc:
            raise InvalidTaskError(f"Player [{author_name}] not found") from exc
    Message.objects.create(
        game=game,
        date=date,
        content=message,
        is_from_master=is_from_master,
        author=author,
    )


@shared_task
def process_roll(
    game_id: int,
    roll_type: RollType,
    date: datetime,
    character_id: int,
    is_combat_initiative: bool = False,
) -> None:
    """
    Process a dice roll.
    """
    logger.info(f"{game_id=}, {roll_type=}, {date=}, {character_id=}")

    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist as exc:
        raise InvalidTaskError(f"Game [{game_id}] not found") from exc
    try:
        character = Character.objects.get(id=character_id, player__game=game)
    except Character.DoesNotExist as exc:
        raise InvalidTaskError(f"Character [{character_id}] not found") from exc

    # Retrieve the corresponding roll request.
    if is_combat_initiative:
        roll_request = CombatInitiativeRequest.objects.filter(
            fighter__character=character, status=RollStatus.PENDING
        ).first()
    else:
        roll_request = RollRequest.objects.filter(
            roll_type=roll_type, character=character, status=RollStatus.PENDING
        ).first()
    roll_request = RollRequest.objects.filter(
        roll_type=roll_type, character=character, status=RollStatus.PENDING
    ).first()
    if roll_request is None:
        raise InvalidTaskError("Roll request not found")

    # Store the roll response.
    if is_combat_initiative:
        roll_response = CombatInitiativeResponse.objects.create(
            game=game, date=date, request=roll_request
        )
    else:
        roll_response = RollResponse.objects.create(
            game=game, date=date, character=character, request=roll_request
        )

    score, result = perform_roll(character, roll_request)
    if is_combat_initiative:
        roll_result = CombatInitiativeResult.objects.create(
            game=game,
            date=date,
            fighter=character.fighter,
            request=roll_request,
            response=roll_response,
            score=score,
        )
    else:
        roll_result = RollResult.objects.create(
            game=game,
            date=date,
            character=character,
            request=roll_request,
            response=roll_response,
            score=score,
            result=result,
        )

    # The corresponding roll request is considered now as done.
    roll_request.status = RollStatus.DONE
    roll_request.save()

    send_to_channel(roll_result)


@shared_task
def check_combat_roll_initiative_complete():
    latest_combat = Combat.objects.all().last()
    for fighter in latest_combat.fighter_set.all():
        logger.info(f"{fighter.character.name=} {fighter.dexterity_check}")
        if fighter.dexterity_check is None:
            logger.info(f"Waiting for {fighter.character.name=}")
            break
    else:
        logger.info("Roll complete!")
        logger.info(f"Initiative order={latest_combat.get_initiative_order()}")
