from django.core.management.base import BaseCommand

from character.tests.factories import CharacterFactory
from user.tests.factories import UserWithPasswordFactory

from ...tests.factories import GameFactory, QuestFactory


class Command(BaseCommand):
    help = "populate the database with representative content"

    def handle(self, *args, **options):
        # Users
        thomas = UserWithPasswordFactory(username="thomas")  # The game master
        eric = UserWithPasswordFactory(username="eric")  # A player
        seb = UserWithPasswordFactory(username="seb")  # Another player

        # Games
        for _ in range(3):
            game = GameFactory(master__user=thomas)
            QuestFactory(game=game)

        # Characters
        CharacterFactory(user=eric, name="Eric")
        CharacterFactory(user=seb, name="Seb")
        for i in range(2, 8):
            CharacterFactory(__sequence=i)

        self.stdout.write(self.style.SUCCESS("Successfully populated the database"))
