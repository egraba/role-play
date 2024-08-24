from django.db.models import TextChoices


class GameState(TextChoices):
    UNDER_PREPARATION = "P", "Under preparation"
    ONGOING = "O", "Ongoing"
