from django.core.management.base import BaseCommand

from character.tests.factories import CharacterFactory
from utils.factories import UserWithPasswordFactory

from ...tests.factories import GameFactory


class Command(BaseCommand):
    help = "populate the database with representative content"

    def handle(self, *args, **options):
        # Users
        thomas = UserWithPasswordFactory(username="thomas")  # The game master
        eric = UserWithPasswordFactory(username="eric")  # A player
        seb = UserWithPasswordFactory(username="seb")  # Another player

        # Games
        for _ in range(3):
            GameFactory(master__user=thomas)

        # Characters
        CharacterFactory(user=eric, name="Eric")
        CharacterFactory(user=seb, name="Seb")
        for i in range(2, 8):
            CharacterFactory(__sequence=i)

        self.stdout.write(self.style.SUCCESS("Successfully populated the database"))
