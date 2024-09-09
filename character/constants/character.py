from django.db.models import IntegerChoices, TextChoices


class Gender(TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    ANDROGYNOUS = "A", "Androgynous"


class CreationState(IntegerChoices):
    BASE_ATTRIBUTES_SELECTION = 1, "base_attributes_selection"
    SKILLS_SELECTION = 2, "skills_selection"
    BACKGROUND_COMPLETION = 3, "background_completion"
    EQUIPMENT_SELECTION = 4, "equipment_selection"
    COMPLETE = 0, "complete"
