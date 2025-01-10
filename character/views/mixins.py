from django.core.cache import cache
from django.http import Http404
from django.views.generic import View
from django.views.generic.list import ContextMixin

from ..models.character import Character
from ..utils.cache import character_key


class CharacterContextMixin(ContextMixin, View):
    """
    Mixin class that provides the character object and contextof the associated
    character's ID given in the view's URL.

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
        except Character.DoesNotExist as e:
            raise Http404(f"Character [{character_id}] does not exist...") from e

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["character"] = self.character
        return context
