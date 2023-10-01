from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView

from character.forms import ChoseEquipmentForm
from character.models.equipment import Equipment
from character.views.mixins import CharacterContextMixin


class ChoseEquipmentView(LoginRequiredMixin, CharacterContextMixin, FormView):
    template_name = "character/choose_equipment.html"
    form_class = ChoseEquipmentForm

    def get_success_url(self):
        return self.character.get_absolute_url()

    def form_valid(self, form):
        Equipment.objects.create(
            name=form.cleaned_data["weapon"], inventory=self.character.inventory
        )
        Equipment.objects.create(
            name=form.cleaned_data["armor"], inventory=self.character.inventory
        )
        return super().form_valid(form)
