from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from .models import Game
from .models import Character
from .models import Narrative
from .models import PendingAction
from .models import DiceLaunch

import random

class IndexView(generic.ListView):
    template_name = 'game/index.html'

    def get_queryset(self):
        return Game.objects.all()

def detail(request, game_id):
    try:
        game = Game.objects.get(pk=game_id)
        character_list = Character.objects.filter(game=game_id)
        narrative_list = Narrative.objects.filter(game=game_id)
        pending_action_list = PendingAction.objects.filter(game=game_id)
        context = {
            'game': game,
            'character_list': character_list,
            'narrative_list': narrative_list,
            'pending_action_list': pending_action_list,
        }
    except Game.DoesNotExist:
        raise Http404(f"Game [{game_id}] does not exist...", game_id)
    return render(request, 'game/game.html', context)

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
        score = random.randint(0, 20)
        dice_launch = DiceLaunch(game=self.game, character=self.character, score=score)
        dice_launch.save()
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
        return HttpResponseRedirect(reverse('detail', args=(self.game_id,)))