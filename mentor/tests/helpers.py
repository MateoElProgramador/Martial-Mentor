from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from mentor.models import Character, Game, UserCharacter
from selenium import webdriver


class MyStaticLiveServerTestCase(StaticLiveServerTestCase):
    """Test case class for Selenium, containing necessary overrides of setUpClass and tearDownClass."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()


def create_game(title, short_title=''):
    return Game.objects.create(title=title, short_title=short_title)


def create_game_and_char(game_title, game_short_title, char_name):
    game = create_game(game_title, game_short_title)
    char = Character.objects.create(name=char_name, game=game)
    return game, char


def create_user_char(user, char, elite_smash):
    return UserCharacter.objects.create(user=user, character=char, elite_smash=elite_smash)


def create_user():
    user = User.objects.create(username='Clive')
    return user
