from django.core.management.base import BaseCommand

from game.models.game import Game, Master


class Command(BaseCommand):
    help = "list all games"

    def handle(self, *args: object, **options: object) -> None:
        games = Game.objects.select_related("master__user").prefetch_related(
            "player_set"
        )
        if not games.exists():
            self.stdout.write("No games found.")
            return

        self.stdout.write(
            f"{'ID':<6} {'Name':<30} {'State':<20} {'Master':<20} {'Players'}"
        )
        self.stdout.write("-" * 85)
        for game in games:
            try:
                master = game.master.user.username
            except Master.DoesNotExist:
                master = "-"
            player_count = len(game.player_set.all())
            self.stdout.write(
                f"{game.id:<6} {game.name:<30} {game.get_state_display():<20} {master:<20} {player_count}"
            )
