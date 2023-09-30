from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404
from django.views.generic import UpdateView, View
from django.views.generic.edit import FormMixin
from django.views.generic.list import ContextMixin

import game.models as gmodels
from character.models.character import Character


class GameContextMixin(ContextMixin, View):
    def is_user_master(self):
        return self.request.user == self.game.master.user

    def is_user_player(self):
        try:
            self.game.player_set.get(character__user=self.request.user)
            return True
        except ObjectDoesNotExist:
            return False

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        game_id = self.kwargs["game_id"]
        try:
            self.game = cache.get(f"game{game_id}")
            if not self.game:
                self.game = gmodels.Game.objects.get(id=game_id)
                cache.set(f"game{game_id}", self.game)
        except ObjectDoesNotExist:
            raise Http404(f"Game [{game_id}] does not exist...")
        if not self.is_user_master() and not self.is_user_player():
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        return context


class GameStatusControlMixin(UpdateView):
    model = gmodels.Game

    def is_user_master(self):
        return self.request.user == self.get_object().master.user


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


class EventContextMixin(GameContextMixin, FormMixin):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if self.game.is_ongoing():
            # Events can be created only when a game is ongoing.
            pass
        else:
            raise PermissionDenied()

    def form_valid(self, form):
        return super().form_valid(form)

    def is_user_master(self):
        return super().is_user_master()
