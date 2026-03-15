from argparse import ArgumentParser

from django.core.management.base import BaseCommand, CommandError

from character.models.character import Character
from user.models import User


class Command(BaseCommand):
    help = "grant XP to a character"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "username", type=str, help="username of the character owner"
        )
        parser.add_argument("amount", type=int, help="XP amount to grant")

    def handle(self, *args: object, **options: object) -> None:
        username = options["username"]
        assert isinstance(username, str)
        amount = options["amount"]
        assert isinstance(amount, int)

        if amount <= 0:
            raise CommandError("amount must be greater than 0")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise CommandError(f"{username=} doesn't exist") from exc

        try:
            character = Character.objects.get(user=user)
        except Character.DoesNotExist as exc:
            raise CommandError(f"{username=} has no character") from exc

        character.increase_xp(amount)
        character.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully granted {amount} XP to {character.name} (total: {character.xp})"
            )
        )
