from argparse import ArgumentParser

from django.core.management.base import BaseCommand, CommandError

from character.models.character import Character
from game.models.game import Game, Player
from user.models import User


class Command(BaseCommand):
    help = "add a player to a game"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("game_id", type=int, help="game ID")
        parser.add_argument("username", type=str, help="username of the player")

    def handle(self, *args: object, **options: object) -> None:
        try:
            game = Game.objects.get(id=options["game_id"])
        except Game.DoesNotExist as exc:
            raise CommandError(f"game id={options['game_id']} doesn't exist") from exc

        username = options["username"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise CommandError(f"{username=} doesn't exist") from exc

        try:
            character = Character.objects.get(user=user)
        except Character.DoesNotExist as exc:
            raise CommandError(f"{username=} has no character") from exc

        if Player.objects.filter(user=user).exists():
            raise CommandError(f"{username=} is already a player in a game")

        Player.objects.create(user=user, game=game, character=character)
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully added player {username} to game {game.id}"
            )
        )
