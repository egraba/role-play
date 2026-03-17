from django.core.management.base import BaseCommand

from character.models.character import Character
from character.tests.factories import CharacterFactory
from game.models.game import Game, Master, Player
from user.tests.factories import UserWithPasswordFactory


class Command(BaseCommand):
    help = "create full test scenario: users, characters, game, and players"

    def handle(self, *args: object, **options: object) -> None:
        thomas = UserWithPasswordFactory(username="thomas")
        eric = UserWithPasswordFactory(username="eric")
        seb = UserWithPasswordFactory(username="seb")

        if not Character.objects.filter(user=eric).exists():
            CharacterFactory(user=eric)
        if not Character.objects.filter(user=seb).exists():
            CharacterFactory(user=seb)

        game, _ = Game.objects.get_or_create(name="Scenario")
        Master.objects.get_or_create(user=thomas, game=game)

        if not Player.objects.filter(user=eric).exists():
            eric_char = Character.objects.filter(user=eric).first()
            Player.objects.create(user=eric, game=game, character=eric_char)

        if not Player.objects.filter(user=seb).exists():
            seb_char = Character.objects.filter(user=seb).first()
            Player.objects.create(user=seb, game=game, character=seb_char)

        self.stdout.write(self.style.SUCCESS("Successfully created scenario"))
