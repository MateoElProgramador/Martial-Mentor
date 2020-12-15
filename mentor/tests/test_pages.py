import time

from django.test import TestCase, LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
import chromedriver_binary  # adds chromedriver binary to path

from mentor.models import snakify
from mentor.tests.helpers import create_game, MyStaticLiveServerTestCase, create_user, login, create_characters


class IndexPageTests(TestCase):

    def test_view_index_page(self):
        """The index page and its content can be viewed."""
        response = self.client.get(reverse('mentor:index'))  # get response for index page
        self.assertEqual(response.status_code, 200)  # check that response code is OK
        self.assertContains(response, "Martial Mentor: the best a combatant can be.")

    def test_game_list_presence(self):
        """A list of games is displayed on the index page."""
        create_game('Super Street Fighter II Turbo', '')
        create_game('Mortal Kombat X', '')

        response = self.client.get(reverse('mentor:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Super Street Fighter II Turbo')
        self.assertContains(response, 'Mortal Kombat X')

    def test_index_with_no_games(self):
        """If no games are in the database, a message is displayed on the index page stating as such."""
        response = self.client.get(reverse('mentor:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No games have been added to the system. Check back soon!')


class ToolsPageTests(MyStaticLiveServerTestCase):

    def test_tools_page(self):
        """A game can be selected from index page, and the user is navigated to the tools page for that game."""
        s = self.selenium
        game = create_game('Mortal Kombat X')

        s.get(self.live_server_url)
        game_anchor = s.find_element_by_link_text(str(game)).click()

        assert 'Mortal Kombat X: Tools' in s.page_source
        assert 'Insights' in s.page_source

    def test_visiting_invalid_tools_page(self):
        """When a URL is entered navigating to a tools page of a game which doesn't exist, a 404 error is displayed."""
        response = self.client.get(reverse('mentor:tools', args=[666]))
        self.assertEqual(response.status_code, 404)
