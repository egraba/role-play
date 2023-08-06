from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, ListView, TemplateView

import character.models as cmodels
import game.models as gmodels
import game.views.mixins as gmixins
import master.models as mmodels


class IndexView(TemplateView):
    template_name = "game/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                context["user_character"] = cmodels.Character.objects.get(
                    user=self.request.user
                )
            except ObjectDoesNotExist:
                pass
        return context


class GameListView(ListView):
    model = gmodels.Game
    paginate_by = 20
    ordering = ["-start_date"]
    template_name = "game/game_list.html"


class GameView(LoginRequiredMixin, ListView, gmixins.GameContextMixin):
    model = gmodels.Event
    paginate_by = 10
    ordering = ["-date"]
    template_name = "game/game.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tale"] = gmodels.Tale.objects.filter(game=self.game.id).last()
        context["instruction"] = gmodels.Instruction.objects.filter(
            game=self.game.id
        ).last()
        context["character_list"] = cmodels.Character.objects.filter(
            player__game=self.game.id
        ).order_by("name")
        try:
            context["player"] = gmodels.Player.objects.get(
                character__user=self.request.user
            )
        except ObjectDoesNotExist:
            pass
        return context

    def get_queryset(self):
        return super().get_queryset().filter(game=self.game.id)


class GameCreateView(LoginRequiredMixin, CreateView):
    model = gmodels.Game
    fields = []
    template_name = "game/game_create.html"

    def post(self, request, *args, **kwargs):
        story_slug = self.kwargs["story_slug"]
        try:
            story = mmodels.Story.objects.get(slug=story_slug)
        except ObjectDoesNotExist:
            return HttpResponseRedirect(
                reverse("game-create-error", args=(story_slug,))
            )
        game = gmodels.Game()
        game.save()
        game.name = f"{story.title} #{game.id}"
        game.story = story
        game.save()
        gmodels.Master.objects.create(user=self.request.user, game=game)
        tale = gmodels.Tale()
        tale.game = game
        tale.message = "The Master created the story."
        tale.content = story.synopsis
        tale.save()
        return HttpResponseRedirect(game.get_absolute_url())


class GameCreateErrorView(LoginRequiredMixin, TemplateView):
    template_name = "game/game_create_error.html"
