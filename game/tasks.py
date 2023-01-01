from celery import shared_task
from django.core.mail import send_mail

from character.models.character import Character
from game.models.events import Choice, DiceLaunch, Instruction
from game.models.game import Game


@shared_task
def send_email(subject, message, from_email, recipient_list):
    return send_mail(subject, message, from_email, recipient_list)


@shared_task
def store_master_instruction(game_id, date, event_message):
    game = Game.objects.get(id=game_id)
    Instruction.objects.create(
        game=game,
        date=date,
        content=event_message,
    )


@shared_task
def store_player_choice(game_id, date, message, character_id, selection):
    game = Game.objects.get(id=game_id)
    character = Character.objects.get(id=character_id)
    Choice.objects.create(
        game=game,
        date=date,
        message=message,
        character=character,
        selection=selection,
    )


@shared_task
def store_player_dice_launch(game_id, date, message, character_id, score):
    game = Game.objects.get(id=game_id)
    character = Character.objects.get(id=character_id)
    DiceLaunch.objects.create(
        game=game,
        date=date,
        message=message,
        character=character,
        score=score,
    )
