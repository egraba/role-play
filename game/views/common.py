from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Exists
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


class GameListView(LoginRequiredMixin, ListView):
    model = gmodels.Game
    paginate_by = 20
    ordering = ["-start_date"]
    template_name = "game/game_list.html"

    def get_queryset(self):
        # The list of games contains those where the user is the master
        # and those where the user is a player.
        qs = super().get_queryset()
        return qs.filter(master__user=self.request.user) | qs.filter(
            Exists(gmodels.Player.objects.filter(character__user=self.request.user))
        )


class GameView(LoginRequiredMixin, ListView, gmixins.GameContextMixin):
    model = gmodels.Event
    paginate_by = 10
    ordering = ["-date"]
    template_name = "game/game.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quest"] = gmodels.Quest.objects.filter(game=self.game.id).last()
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
        campaign_slug = self.kwargs["campaign_slug"]
        try:
            campaign = mmodels.Campaign.objects.get(slug=campaign_slug)
        except ObjectDoesNotExist:
            return HttpResponseRedirect(
                reverse("game-create-error", args=(campaign_slug,))
            )
        game = gmodels.Game()
        game.save()
        game.name = f"{campaign.title} #{game.id}"
        game.campaign = campaign
        game.save()
        gmodels.Master.objects.create(user=self.request.user, game=game)
        quest = gmodels.Quest()
        quest.game = game
        quest.message = "The Master created the campaign."
        quest.content = campaign.synopsis
        quest.save()
        return HttpResponseRedirect(game.get_absolute_url())


class GameCreateErrorView(LoginRequiredMixin, TemplateView):
    template_name = "game/game_create_error.html"
