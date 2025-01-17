from django.contrib import admin

from .models import Character, Game, UserCharacter


class CharacterInline(admin.TabularInline):
    """Allow for characters to be displayed in Game create/edit."""
    model = Character
    extra = 10  # Extra 10 blank character object fields ready to be filled in


class GameAdmin(admin.ModelAdmin):
    inlines = [CharacterInline]


class CharacterAdmin(admin.ModelAdmin):
    # Display name and game title in Character index:
    list_display = ['name', 'game']

    # Display filter at the side for game:
    list_filter = ['game']


class UserCharacterAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_game', 'character', 'elite_smash']


admin.site.register(Game, GameAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(UserCharacter, UserCharacterAdmin)
