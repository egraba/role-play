from django.core.management.base import BaseCommand

from character.models.character import Character

from ...constants.events import RollType
from ...models.game import Game
from ...tests.factories import RollRequestFactory


class Command(BaseCommand):
    help = "request a saving throw from a player"

    def add_arguments(self, parser):
        parser.add_argument("game", type=int)
        parser.add_argument("character", type=int)

    def handle(self, *args, **options):
        game = Game.objects.get(id=options["game"])
        character = Character.objects.get(id=options["character"])
        RollRequestFactory(
            game=game,
            character=character,
            roll_type=RollType.SAVING_THROW,
        )
        self.stdout.write(self.style.SUCCESS("Saving throw created successfully"))
