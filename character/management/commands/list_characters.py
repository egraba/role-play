from django.core.management.base import BaseCommand

from character.models.character import Character


class Command(BaseCommand):
    help = "list all characters"

    def handle(self, *args: object, **options: object) -> None:
        characters = Character.objects.select_related("user", "species").order_by(
            "user__username"
        )
        if not characters.exists():
            self.stdout.write("No characters found.")
            return

        self.stdout.write(
            f"{'Username':<20} {'Character':<20} {'Species':<15} {'Level':<8} {'HP':<12} {'XP'}"
        )
        self.stdout.write("-" * 85)
        for char in characters:
            hp_display = f"{char.hp}/{char.max_hp}"
            species = char.species.name if char.species else "-"
            self.stdout.write(
                f"{char.user.username:<20} {char.name:<20} {species:<15} {char.level:<8} {hp_display:<12} {char.xp}"
            )
