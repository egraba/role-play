from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from .models import Game
from .models import Character
from .models import Narrative
from .models import PendingAction
from .models import DiceLaunch

import asyncio
import random

class IndexView(generic.ListView):
    template_name = 'game/index.html'

    def get_queryset(self):
        return Game.objects.all()

class GameView(generic.ListView):
    model = Game
    template_name = "game/game.html"

    game = None
    character_list = None
    narrative_list = None
    pending_action_list = None

    def setup(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        game_id = self.kwargs['game_id']
        try:
            self.game = Game.objects.get(pk=game_id)
            self.character_list = Character.objects.filter(game=game_id)
            self.narrative_list = Narrative.objects.filter(game=game_id)
            self.pending_action_list = PendingAction.objects.filter(game=game_id)
        except Game.DoesNotExist:
            raise Http404(f"Game [{game_id}] does not exist...", game_id)    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.game
        context['character_list'] = self.character_list
        context['narrative_list'] = self.narrative_list
        context['pending_action_list'] = self.pending_action_list
        return context

class DiceLaunchView(generic.CreateView):
    model = DiceLaunch
    fields = []
    template_name = "game/dice.html"
    object = None
    
    game = None
    game_id = None
    character = None
    character_id = None

    def setup(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.game_id = self.kwargs['game_id']
        self.game = Game.objects.get(pk=self.game_id)
        self.character_id = self.kwargs['character_id']
        self.character = Character.objects.get(pk=self.character_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.game
        context['character'] = self.character
        return context

    def post(self, request, *args, **kwargs):
        dice_launch = DiceLaunch()
        dice_launch.game = self.game
        dice_launch.character = self.character
        dice_launch.score = random.randint(1, 20)
        dice_launch.message = f"{self.character.name} launched a dice: score is {dice_launch.score}!"
        dice_launch.save()
        pending_action = PendingAction.objects.get(character=self.character)
        pending_action.delete()
        return HttpResponseRedirect(reverse('success', args=(self.game_id, self.character_id, dice_launch.pk,)))

class SuccessView(generic.DetailView):
    model = DiceLaunch
    template_name = 'game/success.html'
    
    game = None
    game_id = None
    character = None
    character_id = None

    def setup(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.game_id = self.kwargs['game_id']
        self.game = Game.objects.get(pk=self.game_id)
        self.character_id = self.kwargs['character_id']
        self.character = Character.objects.get(pk=self.character_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.game
        context['character'] = self.character
        return context

    def get_object(self):
        return DiceLaunch.objects.get(pk=self.kwargs.get('action_id'))

    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('game', args=(self.game_id,)))