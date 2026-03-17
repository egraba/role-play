from argparse import ArgumentParser

from django.core.management.base import BaseCommand, CommandError

from game.models.game import Game, Master, Quest
from user.models import User


class Command(BaseCommand):
    help = "create a game for a master user"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("master", type=str, help="username of the game master")

    def handle(self, *args: object, **options: object) -> None:
        username = options["master"]
        assert isinstance(username, str)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise CommandError(f"{username=} doesn't exist") from exc

        game = Game.objects.create(name=f"{username}'s game")
        Master.objects.create(user=user, game=game)
        Quest.objects.create(environment="A new adventure awaits.", game=game)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created game (id={game.id})")
        )
