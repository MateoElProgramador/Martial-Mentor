from django.contrib.auth.models import User
from django.test import TestCase, LiveServerTestCase

from mentor.models import Game, snakify, Character, UserCharacter
from mentor.tests.helpers import create_game, create_game_and_char, create_user, create_user_char


class SnakifyTests(TestCase):
    def test_snakify_with_no_punctuation(self):
        """Returns correctly formatted string, which originally contained no punctuation"""
        new_str = snakify('What a Wonderful World')
        self.assertEqual(new_str, 'what_a_wonderful_world')

    def test_snakify_with_unwanted_punctuation(self):
        """Returns correctly formatted string, removing unwanted punctuation."""
        new_str = snakify('Wh,,a.t a/ Wo/n,d..e!r,f//u?l/ /,W//orld')
        self.assertEqual(new_str, 'what_a_wonderful_world')

    def test_snakify_with_safe_punctuation(self):
        """Returns formatted string, which removes unwanted punctuation whilst keeping 'safe' punctuation."""
        new_str = snakify('Ros(^*ali%na &$( L+um"a')
        self.assertEqual(new_str, 'rosalina_&_luma')


class GameModelTests(TestCase):

    # ----- __str__: ----- #
    def test__str__with_existing_short_title(self):
        """Returns short title when one exists."""
        game = create_game('Super Smash Bros. Brawl', 'Brawl')
        self.assertEqual(str(game), game.short_title)

    def test__str__with_no_short_title(self):
        """Returns title if no short_title exists (empty string)."""
        game = create_game('Super Street Fighter II Turbo', '')
        self.assertEqual(str(game), game.title)

    # ----- img_url: ----- #
    def test_img_url_with_short_title(self):
        """Returns correctly formatted url using game's short_title when it exists."""
        game = create_game('Super Smash Bros. for Wii U', 'Smash 4')
        url = game.img_url()
        self.assertEqual(url, 'mentor/images/games/smash_4/game_cover.png')

    def test_img_url_with_title(self):
        """Returns correctly formatted url using game's title when no short_title exists"""
        game = create_game('Super Smash Bros Melee', '')
        url = game.img_url()
        self.assertEqual(url, 'mentor/images/games/super_smash_bros_melee/game_cover.png')

    def test_img_url_with_punctuation(self):
        """Returns correctly formatted url, with the game title being snakified."""
        game = create_game('Super Smash Bros.: Hero\'s Bla$%de & M(*ight!', '')
        url = game.img_url()
        self.assertEqual(url, 'mentor/images/games/super_smash_bros_heros_blade_&_might/game_cover.png')


class CharacterModelTests(TestCase):

    def test_img_url(self):
        """Returns base url for character, with character name snakified."""
        game = create_game('Super Smash Bros. Ultimate', 'Smash Ultimate')
        char = Character.objects.create(name='Rosalina & Luma', game=game)
        self.assertEqual(char.img_url(), 'games/smash_ultimate/characters/rosalina_&_luma.png')

    def test_rel_img_url(self):
        """Returns relative url for character, with character name snakified."""
        game = create_game('Super Smash Bros. Ultimate', 'Smash Ultimate')
        char = Character.objects.create(name='Pac-Man', game=game)
        rel_url = char.rel_img_url()
        self.assertEqual(rel_url, 'mentor/images/games/smash_ultimate/characters/pac-man.png')


class UserCharacterModelTests(TestCase):

    def test_get_game(self):
        """Returns the Game object related to the character in the given UserCharacter."""
        game, char = create_game_and_char('Street Fighter V', '', 'Ryu')
        user = create_user('Clive')
        user_char = create_user_char(user, char, False)
        self.assertEqual(user_char.get_game(), game)
