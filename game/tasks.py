from celery import shared_task
from django.core.mail import send_mail

from game.models.events import Event
from game.models.game import Game


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
