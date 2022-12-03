from django.http import HttpResponse

from .models import Character

def index(request):
    return HttpResponse("Role play game")

def detail(request, game_id):
    players = Character.objects.all()
    output = players
    return HttpResponse(output)