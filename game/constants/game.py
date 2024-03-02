from django.db.models import TextChoices


class GameStatus(TextChoices):
    UNDER_PREPARATION = "P", "Under preparation"
    ONGOING = "O", "Ongoing"
