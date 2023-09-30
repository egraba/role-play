from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView

from character.forms import ChoseEquipmentForm
from character.views.mixins import CharacterContextMixin


class ChoseEquipmentView(LoginRequiredMixin, CharacterContextMixin, FormView):
    template_name = "character/choose_equipment.html"
    form_class = ChoseEquipmentForm

    def get_success_url(self):
        return self.character.get_absolute_url()

    def form_valid(self, form):
        self.character.save()
        return super().form_valid(form)
