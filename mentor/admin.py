from django.contrib import admin

from .models import Character, Game

admin.site.register([Game, Character])
