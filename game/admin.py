from django.contrib import admin

from .models import Game
from .models import Character
from .models import Narrative
from .models import ActionRequest

class GameAdmin(admin.ModelAdmin):
    fields = ['name']

class CharacterAdmin(admin.ModelAdmin):
    fields = ['game', 'name', 'race', 'age']

class NarrativeAdmin(admin.ModelAdmin):
    fields = ['game', 'message']

class ActionRequestAdmin(admin.ModelAdmin):
    fields = ['narrative', 'character', 'action_type']

admin.site.register(Game, GameAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(Narrative, NarrativeAdmin)
admin.site.register(ActionRequest, ActionRequestAdmin)
