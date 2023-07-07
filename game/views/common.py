from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
)

import chat.models as cmodels
import game.forms as gforms
import game.models as gmodels
import game.views.mixins as gmixins


class IndexView(TemplateView):
    template_name = "game/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                context["user_character"] = gmodels.Character.objects.get(
                    user=self.request.user
                )
            except ObjectDoesNotExist:
                pass
        return context


class ListGameView(ListView):
    model = gmodels.Game
    paginate_by = 20
    ordering = ["-start_date"]
    template_name = "game/gamelist.html"


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
            context["player"] = gmodels.Character.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            pass
        return context

    def get_queryset(self):
        return super().get_queryset().filter(game=self.game.id)


class ListCharacterView(ListView):
    model = gmodels.Character
    paginate_by = 20
    ordering = ["-xp"]
    template_name = "game/characterlist.html"


class DetailCharacterView(DetailView):
    model = gmodels.Character
    template_name = "game/character.html"


class CreateGameView(LoginRequiredMixin, FormView):
    template_name = "game/creategame.html"
    form_class = gforms.CreateGameForm

    def get_success_url(self):
        return reverse_lazy("game", args=(self.game.id,))

    def form_valid(self, form):
        self.game = gmodels.Game()
        self.game.name = form.cleaned_data["name"]
        self.game.master = self.request.user
        self.game.save()
        tale = gmodels.Tale()
        tale.game = self.game
        tale.message = "The Master created the story."
        tale.content = form.cleaned_data["description"]
        tale.save()
        room = cmodels.Room()
        room.game = self.game
        room.save()
        return super().form_valid(form)


class CreateCharacterView(LoginRequiredMixin, CreateView):
    model = gmodels.Character
    form_class = gforms.CreateCharacterForm
    template_name = "game/createcharacter.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            # It is not possible for a user to have several characters.
            gmodels.Character.objects.filter(user=self.request.user).get()
            raise PermissionDenied
        except ObjectDoesNotExist:
            pass

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        character = form.save(commit=False)
        character.user = self.request.user
        character.save()
        return super().form_valid(form)
