from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, ListView

import character.forms as cforms
import character.models as cmodels
import game.models as gmodels


class CharacterDetailView(LoginRequiredMixin, DetailView):
    model = cmodels.Character
    template_name = "character/character.html"


class CharacterListView(LoginRequiredMixin, ListView):
    model = cmodels.Character
    paginate_by = 20
    ordering = ["-xp"]
    template_name = "character/character_list.html"


class CharacterCreateView(LoginRequiredMixin, CreateView):
    model = cmodels.Character
    form_class = cforms.CreateCharacterForm
    template_name = "character/character_create.html"

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        character = form.save()
        gmodels.Player.objects.create(character=character, user=self.request.user)
        return super().form_valid(form)
