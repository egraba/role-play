from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.views.generic import View
from django.views.generic.list import ContextMixin

from character.models.character import Character

from ..utils.cache import character_key


class CharacterContextMixin(ContextMixin, View):
    """
    Mixin class that provides character object and context.

    Attributes:
        character (Character): Character instance.
    """

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        character_id = self.kwargs["character_id"]
        try:
            self.character = cache.get_or_set(
                character_key(character_id), Character.objects.get(id=character_id)
            )
        except ObjectDoesNotExist as e:
            raise Http404(f"Character [{character_id}] does not exist...") from e

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["character"] = self.character
        return context
