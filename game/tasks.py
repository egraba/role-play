from celery import shared_task
from django.core.mail import send_mail

import character.models as cmodels
import game.models as gmodels


@shared_task
def send_email(subject, message, from_email, recipient_list):
    return send_mail(subject, message, from_email, recipient_list)


@shared_task
def store_master_instruction(game_id, date, message, content):
    game = gmodels.Game.objects.get(id=game_id)
    gmodels.Instruction.objects.create(
        game=game,
        date=date,
        message=message,
        content=content,
    )


@shared_task
def store_player_choice(game_id, date, message, character_id, selection):
    game = gmodels.Game.objects.get(id=game_id)
    character = cmodels.Character.objects.get(id=character_id)
    gmodels.Choice.objects.create(
        game=game,
        date=date,
        message=message,
        character=character,
        selection=selection,
    )


@shared_task
def store_player_dice_launch(game_id, date, message, character_id, score):
    game = gmodels.Game.objects.get(id=game_id)
    character = cmodels.Character.objects.get(id=character_id)
    gmodels.DiceLaunch.objects.create(
        game=game,
        date=date,
        message=message,
        character=character,
        score=score,
    )
