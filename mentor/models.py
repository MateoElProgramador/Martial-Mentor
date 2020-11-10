from django.db import models


class Game(models.Model):
    title = models.CharField(max_length=50)
    short_title = models.CharField(max_length=20, blank=True)

    """"""
    def __str__(self):
        return self.short_title if self.short_title != '' else self.title

    def img_url(self):
        return 'images/games/' + self.id + '/game_cover.png'


class Character(models.Model):
    name = models.CharField(max_length=50)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def img_url(self):
        return 'images/games/' + self.game.id + '/characters/' + self.name + '.png'
