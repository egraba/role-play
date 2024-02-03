from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from ...models.character import Character


class Command(BaseCommand):
    help = "delete a user's character"

    def add_arguments(self, parser):
        parser.add_argument("user", type=str, help="character's user")

    def handle(self, *args, **options):
        username = options["user"]
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist as e:
            raise CommandError(f"[{username}] doesn't exist...") from e
        try:
            Character.objects.filter(user=user).delete()
        except ObjectDoesNotExist as e:
            raise CommandError(f"[{username}] doesn't have a character...") from e

        self.stdout.write(self.style.SUCCESS("Successfully deleted the character"))
