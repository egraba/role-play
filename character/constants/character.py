from django.db.models import TextChoices


class Gender(TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    ANDROGYNOUS = "A", "Androgynous"


class CreationState(TextChoices):
    BASE_ATTRIBUTES_SELECTION = "B", "base_attributes_selection"
    COMPLETE = "C", "complete"
