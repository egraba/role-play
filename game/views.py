from django.http import HttpResponse
from django.shortcuts import render

from .models import Game
from .models import Character

def index(request):
    game_list = Game.objects.all()
    context = { 'game_list': game_list}
    return render(request, 'game/index.html', context)

def detail(request, game_id):
    player_list = Character.objects.all()
    context = {
        'game_id': game_id,
        'player_list': player_list
    }
    return render(request, 'game/game.html', context)