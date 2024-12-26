from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import FormView

from .mixins import CharacterContextMixin


class BackgroundCompleteView(LoginRequiredMixin, CharacterContextMixin, FormView):
    """
    This view is used to display the correct form, depending on character's
    selected background, in order to complete character's background information.
    """

    template_name = "character/background_complete.html"

    def get_success_url(self):
        return reverse("equipment-select", args=(self.character.id,))

    def get_initial(self):
        return {"character": self.character}

    def form_valid(self, form):
        return super().form_valid(form)
