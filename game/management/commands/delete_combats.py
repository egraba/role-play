from django.core.management.base import BaseCommand

from game.models.combat import Combat
from game.models.game import Game


class Command(BaseCommand):
    help = "delete all combats of a game"

    def add_arguments(self, parser):
        parser.add_argument("game_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        for game_id in options["game_ids"]:
            try:
                game = Game.objects.get(id=game_id)
            except Game.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Game of {game_id=} not found"))
                raise
            Combat.objects.filter(game=game).delete()
        self.stdout.write(self.style.SUCCESS("Successfully deleted all combats"))
