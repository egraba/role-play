from django.core.management.base import BaseCommand

import utils.testing.factories as utfactories


class Command(BaseCommand):
    help = "populate the database with representative content"

    def handle(self, *args, **options):
        # Users
        thomas = utfactories.UserFactory(username="thomas")  # The game master
        eric = utfactories.UserFactory(username="eric")
        seb = utfactories.UserFactory(username="seb")

        # Games
        for _ in range(5):
            utfactories.GameFactory(master__user=thomas)

        # Characters
        utfactories.CharacterFactory(user=eric)
        utfactories.CharacterFactory(user=seb)
        for _ in range(10):
            utfactories.CharacterFactory()

        self.stdout.write(self.style.SUCCESS("Successfully populated the database"))
