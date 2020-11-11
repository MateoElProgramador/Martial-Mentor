from django.test import TestCase

from mentor.models import Game, snakify, Character


def create_game(title, short_title=''):
    return Game.objects.create(title=title, short_title=short_title)


class SnakifyTests(TestCase):
    def test_snakify_with_no_punctuation(self):
        """Returns correctly formatted string, which originally contained no punctuation"""
        new_str = snakify('What a Wonderful World')
        self.assertEqual(new_str, 'what_a_wonderful_world')

    def test_snakify_with_punctuation(self):
        """Returns correctly formatted string, which originally contained punctuation"""
        new_str = snakify('Wh,,a.t a/ Wo/n,d..er,f//ul //,W//orld')
        self.assertEqual(new_str, 'what_a_wonderful_world')


class GameModelTests(TestCase):

    # __str__:
    def test__str__with_existing_short_title(self):
        """Returns short title when one exists."""
        game = create_game('Super Smash Bros. Brawl', 'Brawl')
        self.assertEqual(str(game), game.short_title)

    def test__str__with_no_short_title(self):
        """Returns title if no short_title exists (empty string)."""
        game = create_game('Super Street Fighter II Turbo', '')
        self.assertEqual(str(game), game.title)

    # img_url:
    def test_img_url_with_short_title(self):
        """Returns correctly formatted url using game's short_title when it exists"""
        game = create_game('Super Smash Bros. for Wii U', 'Smash 4')
        url = game.img_url()
        self.assertEqual(url, 'images/games/smash_4/game_cover.png')

    def test_img_url_with_title(self):
        """Returns correctly formatted url using game's title when no short_title exists"""
        game = create_game('Super Smash Bros. Melee')
        url = game.img_url()
        self.assertEqual(url, 'images/games/super_smash_bros_melee/game_cover.png')


class CharacterModelTests(TestCase):

    def test_img_url(self):
        game = create_game('Super Smash Bros. Ultimate', 'Smash Ultimate')
        char = Character.objects.create(name='Rosalina & Luma', game=game)
        self.assertEqual(char.img_url(), 'images/games/smash_ultimate/characters/rosalina_&_luma.png')