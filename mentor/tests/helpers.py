from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from mentor.models import Character, Game, UserCharacter
from selenium import webdriver

char_names = ['Mario', 'Donkey Kong', 'Link', 'Samus', 'Dark Samus', 'Yoshi',
              'Kirby', 'Fox', 'Pikachu', 'Luigi', 'Ness', 'Captain Falcon',
              'Jigglypuff', 'Peach', 'Daisy', 'Bowser', 'Ice Climbers', 'Sheik',
              'Zelda', 'Dr. Mario', 'Pichu', 'Falco', 'Marth', 'Lucina',
              'Young Link', 'Ganondorf', 'Mewtwo', 'Roy', 'Chrom',
              'Mr. Game & Watch', 'Meta Knight', 'Pit', 'Dark Pit',
              'Zero Suit Samus', 'Wario', 'Snake', 'Ike', 'Pokémon Trainer',
              'Diddy Kong', 'Lucas', 'Sonic', 'King Dedede', 'Olimar', 'Lucario',
              'R.O.B.', 'Toon Link', 'Wolf', 'Villager', 'Mega Man',
              'Wii Fit Trainer', 'Rosalina & Luma', 'Little Mac', 'Greninja',
              'Palutena', 'Pac-Man', 'Robin', 'Shulk', 'Bowser Jr.',
              'Duck Hunt Duo', 'Ryu', 'Ken', 'Cloud', 'Corrin', 'Bayonetta',
              'Inkling', 'Ridley', 'Simon', 'Richter', 'King K. Rool',
              'Isabelle', 'Incineroar', 'Piranha Plant', 'Joker', 'Hero',
              'Banjo & Kazooie', 'Terry', 'Byleth', 'Min Min', 'Steve',
              'Mii Brawler', 'Mii Swordfighter', 'Mii Gunner']


class MyStaticLiveServerTestCase(StaticLiveServerTestCase):
    """Test case class for Selenium, containing necessary overrides of setUpClass and tearDownClass."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        # cls.selenium.quit()
        super().tearDownClass()


def create_game(title, short_title=''):
    return Game.objects.create(title=title, short_title=short_title)


def create_char(name, game):
    return Character.objects.create(name=name, game=game)


def create_game_and_char(game_title, game_short_title, char_name):
    game = create_game(game_title, game_short_title)
    char = Character.objects.create(name=char_name, game=game)
    return game, char


def create_user_char(user, char, elite_smash):
    return UserCharacter.objects.create(user=user, character=char, elite_smash=elite_smash)


def create_user(name, password='123'):
    user = User.objects.create_user(name, password=password)
    return user


def login(selenium, url, username, password_text):
    """Log in using Selenium."""
    selenium.get(url + reverse('login'))

    selenium.find_element_by_name('username').send_keys('Clive')
    selenium.find_element_by_name('password').send_keys('123')
    selenium.find_element_by_xpath('//input[@value="Log In"]').click()


def create_characters(game, char_num, start_ind=0):
    chars = [0] * char_num
    for i, char_name in enumerate(char_names[start_ind:start_ind + char_num]):
        chars[i] = create_char(char_name, game)
    return chars
