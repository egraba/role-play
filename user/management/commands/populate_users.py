from django.core.management.base import BaseCommand

from character.models.character import Character
from character.tests.factories import CharacterFactory
from user.tests.factories import UserWithPasswordFactory


class Command(BaseCommand):
    help = "create test accounts: thomas (DM), eric and seb (with characters)"

    def handle(self, *args: object, **options: object) -> None:
        UserWithPasswordFactory(username="thomas")

        eric = UserWithPasswordFactory(username="eric")
        if not Character.objects.filter(user=eric).exists():
            CharacterFactory(user=eric)

        seb = UserWithPasswordFactory(username="seb")
        if not Character.objects.filter(user=seb).exists():
            CharacterFactory(user=seb)

        self.stdout.write(self.style.SUCCESS("Successfully created test accounts"))
