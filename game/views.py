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
    character_list = Character.objects.all()
    narrative_list = Narrative.objects.all()
    context = {
        'game_id': game_id,
        'character_list': character_list,
        'narrative_list': narrative_list,
    }
    return render(request, 'game/game.html', context)