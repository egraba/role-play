from celery import shared_task
from django.core.mail import send_mail

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
