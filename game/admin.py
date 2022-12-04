from django.contrib import admin

from .models import Game
from .models import Character

class GameAdmin(admin.ModelAdmin):
    fields = ['name']

class CharacterAdmin(admin.ModelAdmin):
    fields = ['game', 'name', 'race', 'age']

admin.site.register(Game, GameAdmin)
admin.site.register(Character, CharacterAdmin)
