import re

from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from mentor.tests.helpers import MyStaticLiveServerTestCase, create_game
import chromedriver_binary  # adds chromedriver binary to path


class InsightsTests(MyStaticLiveServerTestCase):

    # Visit insights page
    # Enter empty slug
    # Enter invalid slug
    # Recent sets
    # Recent placings

    # Invalid second slug
    # Set history between players

    def setUp(self):
        super(InsightsTests, self).setUp()
        self.game = create_game('Super Smash Bros. Ultimate', 'Smash Ultimate')

    def test_nav_from_tools(self):
        """The Insights page for a given game can be navigated to from the Tools page."""
        s = self.selenium
        game = self.game
        server_url = self.live_server_url

        s.get(server_url + reverse('mentor:tools', args=[game.id]))
        s.find_element_by_link_text('Insights').click()

        assert 'Smashgg player slug' in s.page_source

    def test_empty_player_slug(self):
        """If no player slug is entered and the submit button is selected, a validation message is displayed."""
        s = self.selenium
        s.get(self.live_server_url + reverse('mentor:insights', args=[self.game.id]))

        val_message = s.find_element_by_name('slug1').get_attribute('validationMessage')
        self.assertEqual(val_message, 'Please fill in this field.')

    def test_invalid_slug(self):
        """ If an invalid player slug is entered into the form, a message explaining this is displayed in the
            recent sets and recent placings cards."""
        s = self.selenium
        s.get(self.live_server_url + reverse('mentor:insights', args=[self.game.id]))

        s.find_element_by_name('slug1').send_keys('aaaaaaaaaaaaaaaaaaaaaaa')
        s.find_element_by_id('slugSubmit').click()

        sets_errors = s.find_elements_by_id('slug_error_text_sets')
        placements_errors = s.find_elements_by_id('slug_error_text_placements')

        self.assertEqual(len(sets_errors), 1)
        self.assertEqual(len(placements_errors), 1)

    def test_recent_sets(self):
        """When a valid player slug is entered, the recent sets of that player in this game are displayed."""
        s = self.selenium
        s.get(self.live_server_url + reverse('mentor:insights', args=[self.game.id]))

        s.find_element_by_name('slug1').send_keys('a9b92e44')
        s.find_element_by_id('slugSubmit').click()

        # Wait max 5 seconds for recent sets to be retrieved:
        element = WebDriverWait(s, 5).until(
            expected_conditions.presence_of_all_elements_located((By.CLASS_NAME, "recent_set"))
        )

        recent_sets = s.find_elements_by_class_name('recent_set')

        self.assertEqual(len(recent_sets), 15)
        assert 'NaN' not in s.page_source
        assert 'Recent win rate:' in s.page_source

    def test_recent_placings(self):
        """When a valid player slug is entered, the recent tournament placings and stats are displayed."""
        s = self.selenium
        s.get(self.live_server_url + reverse('mentor:insights', args=[self.game.id]))

        s.find_element_by_name('slug1').send_keys('a9b92e44')
        s.find_element_by_id('slugSubmit').click()

        # Wait max 5 seconds for recent placings to be retrieved:
        element = WebDriverWait(s, 5).until(
            expected_conditions.presence_of_all_elements_located((By.CLASS_NAME, "recent_placing"))
        )

        recent_placings = s.find_elements_by_class_name('recent_placing')

        # Check for correct number of occurrences of top percentage and placing for each tournament:
        top_perc_regex = r"\(top \d+%\)"
        placing_regex = r"\d+th"

        top_perc_occs = len(re.findall(top_perc_regex, s.page_source))
        placing_occs = len(re.findall(placing_regex, s.page_source))

        self.assertEqual(top_perc_occs, 15)
        self.assertEqual(placing_occs, 15)

        self.assertEqual(len(recent_placings), 15)
        assert 'NaN' not in s.page_source

    def test_invalid_second_slug(self):
        """When an invalid player slug is entered for the opponent, an error message is displayed."""

