from argparse import ArgumentParser

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from game.constants.game import GameState
from game.models.game import Game


class Command(BaseCommand):
    help = "start a game (set state to ongoing)"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("game_id", type=int, help="game ID")

    def handle(self, *args: object, **options: object) -> None:
        try:
            game = Game.objects.get(id=options["game_id"])
        except Game.DoesNotExist as exc:
            raise CommandError(f"game id={options['game_id']} doesn't exist") from exc

        if game.state == GameState.ONGOING:
            raise CommandError(f"game id={game.id} is already ongoing")

        game.state = GameState.ONGOING
        game.start_date = timezone.now()
        game.save()
        self.stdout.write(self.style.SUCCESS(f"Successfully started game {game.id}"))
