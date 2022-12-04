from django.http import HttpResponse
from django.shortcuts import render

from .models import Game
from .models import Character
from .models import Narrative

def index(request):
    game_list = Game.objects.all()
    context = { 'game_list': game_list}
    return render(request, 'game/index.html', context)

def detail(request, game_id):
    game = Game.objects.get(pk=game_id)
    character_list = Character.objects.filter(game=game_id)
    narrative_list = Narrative.objects.filter(game=game_id)
    context = {
        'game': game,
        'character_list': character_list,
        'narrative_list': narrative_list,
    }
    return render(request, 'game/game.html', context)