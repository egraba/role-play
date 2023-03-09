from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, FormView, ListView, UpdateView

from game.forms import (
    CreateGameForm,
    CreatePendingActionForm,
    CreateTaleForm,
    DamageForm,
    HealForm,
    IncreaseXpForm,
)
from game.models import Character, Game, PendingAction, Tale


class CreateGameView(PermissionRequiredMixin, FormView):
    permission_required = "game.add_game"
    template_name = "game/creategame.html"
    form_class = CreateGameForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        game = Game()
        game.name = form.cleaned_data["name"]
        game.status = "P"
        game.save()
        tale = Tale()
        tale.game = game
        tale.message = "The Master created the story."
        tale.description = form.cleaned_data["description"]
        tale.save()
        return super().form_valid(form)


class AddCharacterView(PermissionRequiredMixin, ListView):
    permission_required = "game.change_character"
    model = Character
    paginate_by = 10
    ordering = ["-xp"]
    template_name = "game/addcharacter.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs["game_id"]
        try:
            context["game"] = Game.objects.get(pk=game_id)
        except Game.DoesNotExist:
            raise Http404(f"Game [{game_id}] does not exist...", game_id)
        return context

    def get_queryset(self):
        return super().get_queryset().filter(game=None)


class AddCharacterConfirmView(PermissionRequiredMixin, UpdateView):
    permission_required = "game.change_character"
    model = Character
    fields = []
    template_name = "game/addcharacterconfirm.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.game_id = self.kwargs["game_id"]
        self.game = Game.objects.get(pk=self.game_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["game"] = self.game
        except Game.DoesNotExist:
            raise Http404(f"Game [{self.game_id}] does not exist...", self.game_id)
        return context

    def post(self, request, *args, **kwargs):
        character = self.get_object()
        character.game = self.game
        character.save()
        return HttpResponseRedirect(
            reverse(
                "game",
                args=(self.game_id,),
            )
        )


class StartGameView(PermissionRequiredMixin, UpdateView):
    permission_required = "game.change_game"
    model = Game
    fields = []
    template_name = "game/startgame.html"

    def post(self, request, *args, **kwargs):
        game = self.get_object()
        character_list = Character.objects.filter(game=game)
        if len(character_list) >= 2:
            game.start_date = timezone.now()
            game.status = "S"
            game.save()
        else:
            raise PermissionDenied("A game must contain at least 2 players...")
        return HttpResponseRedirect(
            reverse(
                "game",
                args=(game.id,),
            )
        )


class EndGameView(PermissionRequiredMixin, UpdateView):
    permission_required = "game.change_game"
    model = Game
    fields = []
    template_name = "game/endgame.html"

    def post(self, request, *args, **kwargs):
        game = self.get_object()
        if game.status == "S":
            game.end_date = timezone.now()
            game.status = "E"
            game.save()
        else:
            raise PermissionDenied("A game must have been started to be ended...")
        return HttpResponseRedirect(
            reverse(
                "game",
                args=(game.id,),
            )
        )


class CreateTaleView(PermissionRequiredMixin, FormView):
    permission_required = "game.change_game"
    model = Tale
    fields = ["description"]
    template_name = "game/createtale.html"
    form_class = CreateTaleForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.game_id = self.kwargs["game_id"]
        self.game = Game.objects.get(pk=self.game_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        return context

    def post(self, request, *args, **kwargs):
        form = CreateTaleForm(request.POST)
        if form.is_valid():
            tale = Tale()
            tale.game = self.game
            tale.message = "The Master updated the story."
            tale.description = form.cleaned_data["description"]
            tale.save()
            return HttpResponseRedirect(reverse("game", args=(self.game_id,)))


class CreatePendingActionView(PermissionRequiredMixin, CreateView):
    permission_required = "game.change_pending_action"
    model = PendingAction
    form_class = CreatePendingActionForm
    template_name = "game/creatependingaction.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.game_id = self.kwargs["game_id"]
            self.game = Game.objects.get(id=self.game_id)
        except Game.DoesNotExist:
            raise Http404(f"Game [{self.game_id}] does not exist...", self.game_id)
        try:
            self.character_id = self.kwargs["character_id"]
            self.character = Character.objects.get(id=self.character_id, game=self.game)
        except Character.DoesNotExist:
            raise Http404(
                f"Character [{self.character_id}] does not exist...", self.character_id
            )

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game_id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        context["character"] = self.character
        return context

    def form_valid(self, form):
        pending_action_list = PendingAction.objects.filter(character=self.character)
        if len(pending_action_list) == 0:
            pending_action = form.save(commit=False)
            pending_action.game = self.game
            pending_action.character = self.character
            pending_action.date = timezone.now()
            pending_action.message = f"{self.character} needs to perform an action: {pending_action.get_action_type_display()}"
            pending_action.save()
        else:
            raise PermissionDenied
        return super().form_valid(form)


class IncreaseXpView(PermissionRequiredMixin, FormView):
    permission_required = "game.change_character"
    form_class = IncreaseXpForm
    template_name = "game/xp.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.game_id = self.kwargs["game_id"]
            self.game = Game.objects.get(id=self.game_id)
        except Game.DoesNotExist:
            raise Http404(f"Game [{self.game_id}] does not exist...", self.game_id)
        try:
            self.character_id = self.kwargs["character_id"]
            self.character = Character.objects.get(id=self.character_id, game=self.game)
        except Character.DoesNotExist:
            raise Http404(
                f"Character [{self.character_id}] does not exist...", self.character_id
            )

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game_id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        context["character"] = self.character
        return context

    def form_valid(self, form):
        self.character.xp += form.cleaned_data["xp"]
        self.character.save()
        return super().form_valid(form)


class DamageView(PermissionRequiredMixin, FormView):
    permission_required = "game.change_character"
    form_class = DamageForm
    template_name = "game/damage.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.game_id = self.kwargs["game_id"]
            self.game = Game.objects.get(id=self.game_id)
        except Game.DoesNotExist:
            raise Http404(f"Game [{self.game_id}] does not exist...", self.game_id)
        try:
            self.character_id = self.kwargs["character_id"]
            self.character = Character.objects.get(id=self.character_id, game=self.game)
        except Character.DoesNotExist:
            raise Http404(
                f"Character [{self.character_id}] does not exist...", self.character_id
            )

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game_id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        context["character"] = self.character
        return context

    def form_valid(self, form):
        self.character.hp -= form.cleaned_data["hp"]
        self.character.save()
        return super().form_valid(form)


class HealView(PermissionRequiredMixin, FormView):
    permission_required = "game.change_character"
    form_class = HealForm
    template_name = "game/heal.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.game_id = self.kwargs["game_id"]
            self.game = Game.objects.get(id=self.game_id)
        except Game.DoesNotExist:
            raise Http404(f"Game [{self.game_id}] does not exist...", self.game_id)
        try:
            self.character_id = self.kwargs["character_id"]
            self.character = Character.objects.get(id=self.character_id, game=self.game)
        except Character.DoesNotExist:
            raise Http404(
                f"Character [{self.character_id}] does not exist...", self.character_id
            )

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game_id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        context["character"] = self.character
        return context

    def form_valid(self, form):
        healing_points = form.cleaned_data["hp"]
        if healing_points + self.character.hp <= self.character.max_hp:
            self.character.hp += healing_points
        else:
            self.character.hp = self.character.max_hp
        self.character.save()
        return super().form_valid(form)
