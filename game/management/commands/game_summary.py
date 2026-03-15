from argparse import ArgumentParser

from django.core.management.base import BaseCommand, CommandError

from game.models.combat import Combat
from game.models.game import Game, Master


class Command(BaseCommand):
    help = "show a detailed summary of a game"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("game_id", type=int, help="game ID")

    def handle(self, *args: object, **options: object) -> None:
        try:
            game = (
                Game.objects.select_related("master__user")
                .prefetch_related("player_set__user", "player_set__character")
                .get(id=options["game_id"])
            )
        except Game.DoesNotExist as exc:
            raise CommandError(f"game id={options['game_id']} doesn't exist") from exc

        self.stdout.write(f"Game: {game.name} (id={game.id})")
        self.stdout.write(f"State: {game.get_state_display()}")
        if game.start_date:
            self.stdout.write(f"Started: {game.start_date:%Y-%m-%d %H:%M}")

        try:
            master = game.master.user.username
        except Master.DoesNotExist:
            master = "-"
        self.stdout.write(f"Master: {master}")

        players = game.player_set.all()
        if players.exists():
            self.stdout.write("\nPlayers:")
            self.stdout.write(f"  {'Username':<20} {'Character':<20} {'HP':<12} {'XP'}")
            self.stdout.write("  " + "-" * 60)
            for player in players:
                char = player.character
                hp_display = f"{char.hp}/{char.max_hp}"
                self.stdout.write(
                    f"  {player.user.username:<20} {char.name:<20} {hp_display:<12} {char.xp}"
                )
        else:
            self.stdout.write("\nNo players.")

        combat_count = Combat.objects.filter(game=game).count()
        self.stdout.write(f"\nActive combats: {combat_count}")
