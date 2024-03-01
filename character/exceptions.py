from django.core.exceptions import ObjectDoesNotExist


class AbilityNotFound(ObjectDoesNotExist):
    """Raised when an ability is not found."""

    def __init__(self, ability_type):
        self.message = f"[{ability_type}] is not found..."
        super().__init__(self.message)
