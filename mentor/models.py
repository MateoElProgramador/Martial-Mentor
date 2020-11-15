from django.contrib.auth.models import User
from django.db import models


def snakify(x):
    x = str(x)  # ensure an object isn't asked to execute string methods (no type assumptions made)
    banned_chars = ['.', ',', '/', '-']
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

    # TODO: Change in line with Character img_url
    def img_url(self):
        return 'mentor/images/games/' + snakify(str(self)) + '/game_cover.png'


class Character(models.Model):
    name = models.CharField(max_length=50)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def img_url(self):
        """ Return path of image, leaving out the start section which distinguishes
            between static url and root path."""
        return 'games/' + snakify(self.game) + '/characters/' + snakify(self.name) + '.png'

    def rel_img_url(self):
        """Return relative URL of image, for use in templates."""
        return 'mentor/images/' + self.img_url()


class UserCharacter(models.Model):
    """Model used to track users' elite smash status for each character."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    elite_smash = models.BooleanField(default=False)

    def get_game(self):
        """ Shorthand to easily access the game of the given UserCharacter.
            Also used as a column on admin page. """
        return self.character.game
