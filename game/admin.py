from django.contrib import admin

from .models import Game
from .models import Character

admin.site.register(Game)
admin.site.register(Character)
