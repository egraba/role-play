from django.contrib import admin

from .models import Game
from .models import Character

class GameAdmin(admin.ModelAdmin):
    fields = ['name']

admin.site.register(Game, GameAdmin)
admin.site.register(Character)
