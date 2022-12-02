from django.http import HttpResponse

def index(request):
    return HttpResponse("Role play game")

def detail(request, game_id):
    return HttpResponse("Game ID %s" % game_id)