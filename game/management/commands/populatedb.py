from django.core.management.base import BaseCommand

from utils.factories import CharacterFactory, GameFactory, UserFactory


class Command(BaseCommand):
    help = "populate the database with representative content"

    def handle(self, *args, **options):
        # Users
        thomas = UserFactory(username="thomas")  # The game master
        eric = UserFactory(username="eric")
        seb = UserFactory(username="seb")

        # Games
        for _ in range(5):
            GameFactory(master__user=thomas)

        # Characters
        CharacterFactory(user=eric)
        CharacterFactory(user=seb)
        for _ in range(10):
            CharacterFactory()

        self.stdout.write(self.style.SUCCESS("Successfully populated the database"))
