from django.db.models import TextChoices


class Gender(TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    ANDROGYNOUS = "A", "Androgynous"
