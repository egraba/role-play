from django.core.management.base import BaseCommand, CommandError

from user.models import User

from ...models.character import Character


class Command(BaseCommand):
    help = "delete a user's character"

    def add_arguments(self, parser):
        parser.add_argument("user", type=str, help="character's user")

    def handle(self, *args, **options):
        username = options["user"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise CommandError(f"[{username}] doesn't exist") from exc
        Character.objects.filter(user=user).delete()
        self.stdout.write(self.style.SUCCESS("Successfully deleted the character"))
