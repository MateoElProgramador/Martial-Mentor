from django.contrib.auth.models import User
from django.db import models


def snakify(x):
    x = str(x)  # ensure an object isn't asked to execute string methods (no type assumptions made)
    banned_chars = ['.', ',', '/', ]
    for c in banned_chars:
        x = x.replace(c, '')
    x = x.replace(' ', '_').lower()  # replace spaces with underscores
    return x


class Game(models.Model):
    title = models.CharField(max_length=50)
    short_title = models.CharField(max_length=20, blank=True)

    def __str__(self):
        """Return short title if not blank, else return title."""
        return self.short_title if self.short_title != '' else self.title

    def img_url(self):
        return 'mentor/images/games/' + snakify(str(self)) + '/game_cover.png'


class Character(models.Model):
    name = models.CharField(max_length=50)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def img_url(self):
        return 'mentor/images/games/' + snakify(self.game) + '/characters/' + snakify(self.name) + '.png'


class UserCharacter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    elite_smash = models.BooleanField(default=False)

    def get_game(self):
        return self.character.game

