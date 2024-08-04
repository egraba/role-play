from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Exists
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, ListView, TemplateView

from character.constants.abilities import AbilityName
from character.models.character import Character
from master.models import Campaign

from ..constants.events import RollStatus, RollType
from ..flows import GameFlow
from ..models.events import Event, QuestUpdate, RollRequest
from ..models.game import Game, Master, Player
from ..views.mixins import GameContextMixin


class IndexView(TemplateView):
    template_name = "game/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                context["user_character"] = Character.objects.get(
                    user=self.request.user
                )
            except ObjectDoesNotExist:
                pass
        return context


class GameListView(LoginRequiredMixin, ListView):
    model = Game
    paginate_by = 20
    ordering = ["-start_date"]
    template_name = "game/game_list.html"

    def get_queryset(self):
        # The list of games contains those where the user is the master
        # and those where the user is a player.
        qs = super().get_queryset()
        return qs.filter(master__user=self.request.user) | qs.filter(
            Exists(Player.objects.filter(character__user=self.request.user))
        )


class GameView(LoginRequiredMixin, ListView, GameContextMixin):
    model = Event
    paginate_by = 10
    ordering = ["-date"]
    template_name = "game/game.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["flow"] = GameFlow(self.game)
        context["quest"] = QuestUpdate.objects.filter(game=self.game.id).last()
        context["character_list"] = Character.objects.filter(
            player__game=self.game.id
        ).order_by("name")
        try:
            current_player = Player.objects.get(character__user=self.request.user)
            context["player"] = current_player
            context["ability_check_request"] = RollRequest.objects.filter(
                character__player=current_player,
                roll_type=RollType.ABILITY_CHECK,
                status=RollStatus.PENDING,
                is_combat=False,
            ).first()
            context["combat_initiative_request"] = RollRequest.objects.filter(
                character__player=current_player,
                roll_type=RollType.ABILITY_CHECK,
                ability_type=AbilityName.DEXTERITY,
                status=RollStatus.PENDING,
                is_combat=True,
            ).first()
            context["saving_throw_request"] = RollRequest.objects.filter(
                character__player=current_player,
                roll_type=RollType.SAVING_THROW,
                status=RollStatus.PENDING,
            ).first()
        except Player.DoesNotExist:
            pass
        return context

    def get_queryset(self):
        return super().get_queryset().filter(game=self.game.id).select_subclasses()


class GameCreateView(LoginRequiredMixin, CreateView):
    model = Game
    fields = []  # type: list[str]
    template_name = "game/game_create.html"

    def post(self, request, *args, **kwargs):
        campaign_slug = self.kwargs["campaign_slug"]
        try:
            campaign = Campaign.objects.get(slug=campaign_slug)
        except ObjectDoesNotExist:
            return HttpResponseRedirect(
                reverse("game-create-error", args=(campaign_slug,))
            )
        game = Game()
        game.save()
        game.name = f"{campaign.title} #{game.id}"
        game.campaign = campaign
        game.save()
        Master.objects.create(user=self.request.user, game=game)
        quest_update = QuestUpdate()
        quest_update.game = game
        quest_update.content = campaign.synopsis
        quest_update.save()
        return HttpResponseRedirect(game.get_absolute_url())


class GameCreateErrorView(LoginRequiredMixin, TemplateView):
    template_name = "game/game_create_error.html"
