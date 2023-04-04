from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DetailView, ListView

import game.models as gmodels
import game.views.mixins as gmixins


class IndexView(ListView):
    model = gmodels.Game
    paginate_by = 5
    ordering = ["-start_date"]
    template_name = "game/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                context["character"] = gmodels.Character.objects.filter(
                    user=self.request.user
                ).last()
            except ObjectDoesNotExist:
                pass
        return context

    def get_queryset(self):
        if self.request.user.has_perm("game.add_game"):
            return super().get_queryset().filter(user=self.request.user)
        elif self.request.user.has_perm("game.add_character"):
            return super().get_queryset().filter(character__user=self.request.user)
        else:
            return super().get_queryset().none()


class GameView(LoginRequiredMixin, ListView, gmixins.GameContextMixin):
    model = gmodels.Event
    paginate_by = 20
    ordering = ["-date"]
    template_name = "game/game.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tale"] = gmodels.Tale.objects.filter(game=self.game.id).last()
        context["character_list"] = gmodels.Character.objects.filter(
            game=self.game.id
        ).order_by("name")
        try:
            player = gmodels.Character.objects.get(user=self.request.user)
            context["player"] = player
            context["pending_action"] = gmodels.PendingAction.objects.filter(
                game=self.game.id, character=player
            ).get()
        except ObjectDoesNotExist:
            pass
        return context

    def get_queryset(self):
        return super().get_queryset().filter(game=self.game.id)


class DetailCharacterView(DetailView):
    model = gmodels.Character
    template_name = "game/character.html"
