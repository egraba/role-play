from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Game
from .models import Character
from .models import Narrative
from .models import ActionRequest
from .models import DiceLaunch

import random

def index(request):
    game_list = Game.objects.all()
    context = { 'game_list': game_list}
    return render(request, 'game/index.html', context)

def detail(request, game_id):
    game = Game.objects.get(pk=game_id)
    character_list = Character.objects.filter(game=game_id)
    narrative_list = Narrative.objects.filter(game=game_id)
    action_request_list = ActionRequest.objects.filter(game=game_id)
    context = {
        'game': game,
        'character_list': character_list,
        'narrative_list': narrative_list,
        'action_request_list': action_request_list,
    }
    return render(request, 'game/game.html', context)

def launch_dice_request(request, game_id, character_id):
    game = Game.objects.get(pk=game_id)
    character = Character.objects.get(pk=character_id)
    context = {
        'game': game,
        'character': character,
    }
    return render(request, 'game/dice.html', context)

def launch_dice(request, game_id, character_id):
    character = Character.objects.get(pk=character_id)
    score = random.randint(0, 20)
    dice_launch = DiceLaunch.objects.create(character=character, score=score)
    dice_launch.save()
    return HttpResponseRedirect(reverse('detail', args=(game_id,)))
