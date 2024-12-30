from datetime import datetime

from celery import shared_task
from celery.exceptions import InvalidTaskError
from celery.utils.log import get_task_logger
from django.core.cache import cache
from django.core.mail import send_mail as django_send_mail
from django_celery_beat.models import PeriodicTask

from character.models.character import Character

from .constants.events import RollStatus, RollType
from .models.combat import Combat
from .models.events import (
    CombatInitativeOrderSet,
    CombatInitiativeRequest,
    CombatInitiativeResponse,
    CombatInitiativeResult,
    Message,
    RollRequest,
    RollResponse,
    RollResult,
)
from .models.game import Game, Player, Master
from .rolls import perform_combat_initiative_roll, perform_roll
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
    author_str: str,
) -> None:
    """
    Store the message received in the channel.
    """
    logger.info(f"{game_id=}, {date=}, {message=}")
    try:
        game = cache.get_or_set(game_key(game_id), Game.objects.get(id=game_id))
    except Game.DoesNotExist as exc:
        raise InvalidTaskError(f"Game of {game_id=} not found") from exc
    if Master.objects.filter(game=game, user__username=author_str).exists():
        try:
            author = Master.objects.get(game=game, user__username=author_str)
        except Master.DoesNotExist as exc:
            raise InvalidTaskError(f"{author_str} not found") from exc
    elif Player.objects.filter(game=game, user__username=author_str).exists():
        try:
            author = Player.objects.get(game=game, user__username=author_str)
        except Player.DoesNotExist as exc:
            raise InvalidTaskError(f"{author_str=} not found") from exc
    else:
        raise InvalidTaskError(f"{author_str} is not a supported actor")
    Message.objects.create(
        game=game,
        date=date,
        content=message,
        author=author,
    )


@shared_task
def process_roll(
    game_id: int,
    author_id: int,
    date: datetime,
    roll_type: RollType,
) -> None:
    """
    Process a dice roll.
    """
    logger.info(f"{game_id=}, {author_id=}, {roll_type=}, {date=}")

    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist as exc:
        raise InvalidTaskError(f"Game of {game_id=} not found") from exc
    try:
        player = Player.objects.get(actor_ptr_id=author_id, game=game)
    except Player.DoesNotExist as exc:
        raise InvalidTaskError(f"Player of {author_id=} not found") from exc

    # Retrieve the corresponding roll request.
    roll_request = RollRequest.objects.filter(
        roll_type=roll_type, player=player, status=RollStatus.PENDING
    ).first()
    if roll_request is None:
        raise InvalidTaskError("Roll request not found")
    logger.info(f"{roll_request=}, {roll_request.player=}")

    # Store the roll response.
    roll_response = RollResponse.objects.create(
        game=game, author=player, date=date, player=player, request=roll_request
    )
    logger.info(f"{roll_response.request=}")

    score, result = perform_roll(player, roll_request)
    roll_result = RollResult.objects.create(
        game=game,
        author=player.actor_ptr,
        date=date,
        player=player,
        request=roll_request,
        response=roll_response,
        score=score,
        result=result,
    )

    # The corresponding roll request is considered now as done.
    roll_request.status = RollStatus.DONE
    roll_request.save()

    logger.info(f"{roll_result.request=}, {roll_result.score=}, {roll_result.result=}")
    send_to_channel(roll_result)


@shared_task
def process_combat_initiative_roll(
    game_id: int,
    roll_type: RollType,
    date: datetime,
    character_id: int,
) -> None:
    """
    Process a dice roll for combat initiative.
    """
    logger.info(f"{game_id=}, {roll_type=}, {date=}, {character_id=}")

    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist as exc:
        raise InvalidTaskError(f"Game of {game_id=} not found") from exc
    try:
        character = Character.objects.get(id=character_id, player__game=game)
    except Character.DoesNotExist as exc:
        raise InvalidTaskError(f"Character of {character_id=} not found") from exc

    # Retrieve the corresponding roll request.
    roll_request = CombatInitiativeRequest.objects.filter(
        fighter__character=character, status=RollStatus.PENDING
    ).first()
    if roll_request is None:
        raise InvalidTaskError("Roll request not found")
    logger.info(f"{roll_request=}, {roll_request.fighter=}")

    # Store the roll response.
    roll_response = CombatInitiativeResponse.objects.create(
        game=game, date=date, request=roll_request
    )
    logger.info(f"{roll_response.request=}")

    score = perform_combat_initiative_roll(roll_request.fighter)
    roll_result = CombatInitiativeResult.objects.create(
        game=game,
        date=date,
        fighter=roll_request.fighter,
        request=roll_request,
        response=roll_response,
        score=score,
    )

    # The corresponding roll request is considered now as done.
    roll_request.status = RollStatus.DONE
    roll_request.save()

    logger.info(f"{roll_result.request=}, {roll_result.score=}")
    send_to_channel(roll_result)


@shared_task
def check_combat_roll_initiative_complete():
    latest_combat = Combat.objects.all().last()
    if latest_combat is None:
        logger.info("No combat to check")
        pass
    else:
        for fighter in latest_combat.fighter_set.all():
            logger.info(f"{fighter.character.name=} {fighter.dexterity_check}")
            if fighter.dexterity_check is None:
                logger.info(f"Waiting for {fighter.character.name=}")
                break
        else:
            logger.info("Roll complete!")
            logger.info(f"Initiative order={latest_combat.get_initiative_order()}")
            initiative_order_set, created = (
                CombatInitativeOrderSet.objects.get_or_create(
                    combat=latest_combat,
                    game=latest_combat.game,
                )
            )
            if created:
                periodic_task = PeriodicTask.objects.get(
                    name__startswith=f"game{latest_combat.game.id}"
                )
                periodic_task.enabled = False
                periodic_task.save()
                send_to_channel(initiative_order_set)
