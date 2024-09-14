from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.views.generic import FormView

from ..constants.backgrounds import Background
from ..forms.backgrounds import (
    AcolyteForm,
    CriminalForm,
    FolkHeroForm,
    NobleForm,
    SageForm,
    SoldierForm,
)
from .mixins import CharacterContextMixin


class BackgroundCompleteView(LoginRequiredMixin, CharacterContextMixin, FormView):
    """
    This view is used to display the correct form, depending on character's
    selected background, in order to complete character's background information.
    """

    template_name = "character/background_complete.html"

    def get_success_url(self):
        return reverse("equipment-select", args=(self.character.id,))

    def get_form_class(self):
        match self.character.background:
            case Background.ACOLYTE:
                form_class = AcolyteForm
            case Background.CRIMINAL:
                form_class = CriminalForm
            case Background.FOLK_HERO:
                form_class = FolkHeroForm
            case Background.NOBLE:
                form_class = NobleForm
            case Background.SAGE:
                form_class = SageForm
            case Background.SOLDIER:
                form_class = SoldierForm
            case _:
                raise ValidationError(
                    "The selected background has no corresponding form..."
                )
        return form_class

    def get_initial(self):
        return {"character": self.character}

    def form_valid(self, form):
        return super().form_valid(form)
