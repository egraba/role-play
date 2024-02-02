from celery import shared_task
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.utils import timezone

from character.models.character import Character
from game.models.events import AbilityCheck, AbilityCheckRequest, Event
from game.models.game import Game

from .schemas import GameEventType, PlayerType
from .utils.channels import send_to_channel
from .utils.dice_rolls import perform_ability_check


@shared_task
def send_email(subject, message, from_email, recipient_list):
    return send_mail(subject, message, from_email, recipient_list)


@shared_task
def store_message(game_id, date, message):
    game = Game.objects.get(id=game_id)
    Event.objects.create(
        game=game,
        date=date,
        message=message,
    )


@shared_task
def process_ability_check(game_id, date, character_id, message):
    game = Game.objects.get(id=game_id)
    character = Character.objects.get(id=character_id)

    # Retrieve the corresponding request.
    ability_check_request = AbilityCheckRequest.objects.filter(
        character=character, status=AbilityCheckRequest.Status.PENDING
    ).first()
    if ability_check_request is None:
        raise PermissionDenied

    score, result = perform_ability_check(character, ability_check_request)
    ability_check = AbilityCheck.objects.create(
        game=game,
        date=date,
        character=character,
        request=ability_check_request,
        message=f"score: {score}, ability check result: {result}",
        result=result,
    )

    # The corresponding request is done.
    ability_check_request.status = AbilityCheckRequest.Status.DONE
    ability_check_request.save()

    send_to_channel(
        game_id=game.id,
        game_event={
            "type": GameEventType.ABILITY_CHECK_RESULT,
            "player_type": PlayerType.MASTER,
            "date": timezone.now().isoformat(),
            "message": ability_check.message,
        },
    )
