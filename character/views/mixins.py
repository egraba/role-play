from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.views.generic import View
from django.views.generic.list import ContextMixin

from character.models.character import Character


class CharacterContextMixin(ContextMixin, View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        character_id = self.kwargs["character_id"]
        try:
            self.character = cache.get(f"character{character_id}")
            if not self.character:
                self.character = Character.objects.get(id=character_id)
                cache.set(f"character{character_id}", self.character)
        except ObjectDoesNotExist:
            raise Http404(f"Character [{character_id}] does not exist...")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["character"] = self.character
        return context
