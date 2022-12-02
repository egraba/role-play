from django.contrib import admin

from .models import Game
from .models import Master
from .models import Character

admin.site.register(Game)
admin.site.register(Master)
admin.site.register(Character)
