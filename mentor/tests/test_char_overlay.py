import time
from django.urls import reverse
from mentor.models import snakify
from mentor.tests.helpers import create_characters, login, MyStaticLiveServerTestCase, create_game, create_user
import chromedriver_binary  # adds chromedriver binary to path


class CharOverlayTests(MyStaticLiveServerTestCase):

    def setUp(self):
        super(CharOverlayTests, self).setUp()
        self.game = create_game('Super Smash Bros. Ultimate', 'Smash Ultimate')
        self.user = create_user('Clive', password='123')

    def test_nav_from_tools_not_logged_in(self):
        """ If a non-logged in user selects the character overlay link from the tools page,
            they are redirected to the login page."""
        s = self.selenium
        game = self.game
        s.get(self.live_server_url + reverse('mentor:tools', args=[game.id]))

        overlay_link = s.find_element_by_xpath("//body//a[text()='Character icon overlay']")
        overlay_link.click()

        assert 'Forgotten your password?' in s.page_source

    def test_nav_from_tools_logged_in(self):
        """If a logged in user selects character overlay link from tools page, character overlay page is displayed."""
        s = self.selenium
        game = self.game
        server_url = self.live_server_url

        # Log in using helper method::
        login(s, server_url, self.user.username)

        # Navigate to tools for given game:
        s.get(server_url + reverse('mentor:tools', args=[game.id]))

        # Select character overlay link:
        overlay_link = s.find_element_by_xpath("//body//a[text()='Character icon overlay']")
        overlay_link.click()

        # Ensure that character overlay page has been reached:
        assert 'Smash Ultimate: Character Overlay' in s.page_source

    def test_char_overlay_no_characters(self):
        """ If the character overlay page is visited and no characters exist for the given game,
            a message explaining this is displayed."""
        s = self.selenium
        server_url = self.live_server_url
        game = self.game

        # Log in using helper method::
        login(s, server_url, self.user.username)
        s.get(server_url + reverse('mentor:char_overlay', args=[game.id]))
        assert 'No characters exist for ' + str(game) + ' yet, please check back later!' in s.page_source

    def test_char_overlay_invalid_game(self):
        """If the URL points to a game which doesn't exist, a 404 error is displayed."""
        s = self.selenium
        s_url = self.live_server_url

        login(s, s_url, self.user.username)
        s.get(s_url + reverse('mentor:char_overlay', args=[666]))
        assert 'Not Found' in s.page_source

    def test_char_overlay_display_one_container(self):
        """If there are fewer than 60 characters, the character icons are displayed in a single container."""
        s = self.selenium
        server_url = self.live_server_url
        game = self.game

        # Create characters:
        chars = create_characters(game, 5)

        login(s, server_url, self.user.username)
        s.get(server_url + reverse('mentor:char_overlay', args=[game.id]))

        # Check number of imgs in lone_char_container:
        lone_container_imgs = s.find_elements_by_xpath("//*[@id='lone_char_container']/a")
        self.assertEqual(len(lone_container_imgs), 5)

        # Check number of imgs in top_char_container:
        top_container_imgs = s.find_elements_by_xpath("//*[@id='top_char_container']/a")
        self.assertEqual(len(top_container_imgs), 0)

        # Check number of imgs in side_char_container:
        side_container_imgs = s.find_elements_by_xpath("//*[@id='side_char_container']/a")
        self.assertEqual(len(side_container_imgs), 0)

    def test_char_overlay_display_two_containers(self):
        """If there are more than 60 characters,  the character icons are displayed in 'top' and 'side' containers."""
        s = self.selenium
        server_url = self.live_server_url
        game = self.game

        # Create characters:
        chars = create_characters(game, 75)

        login(s, server_url, self.user.username)
        s.get(server_url + reverse('mentor:char_overlay', args=[game.id]))

        # Check number of imgs in lone_char_container:
        lone_container_imgs = s.find_elements_by_xpath("//*[@id='lone_char_container']/a")
        self.assertEqual(len(lone_container_imgs), 0)

        # Check number of imgs in top_char_container:
        top_container_imgs = s.find_elements_by_xpath("//*[@id='top_char_container']/a")
        self.assertEqual(len(top_container_imgs), 62)

        # Check number of imgs in side_char_container:
        side_container_imgs = s.find_elements_by_xpath("//*[@id='side_char_container']/a")
        self.assertEqual(len(side_container_imgs), 13)

    def test_char_overlay_61_characters(self):
        """If there are 61 characters, the character icons are displayed correctly."""
        """This test is due to a [:62] slicing operation which occurs with > 60 characters."""
        s = self.selenium
        server_url = self.live_server_url
        game = self.game

        # Create characters:
        chars = create_characters(game, 61)

        login(s, server_url, self.user.username)
        s.get(server_url + reverse('mentor:char_overlay', args=[game.id]))

        # Check number of imgs in lone_char_container:
        lone_container_imgs = s.find_elements_by_xpath("//*[@id='lone_char_container']/a")
        self.assertEqual(len(lone_container_imgs), 0)

        # Check number of imgs in top_char_container:
        top_container_imgs = s.find_elements_by_xpath("//*[@id='top_char_container']/a")
        self.assertEqual(len(top_container_imgs), 61)

        # Check number of imgs in side_char_container:
        side_container_imgs = s.find_elements_by_xpath("//*[@id='side_char_container']/a")
        self.assertEqual(len(side_container_imgs), 0)

        # Add 4 more more characters, bringing it to 65 characters:
        # chars += create_characters(game, 4, start_ind=61)
        #
        # s.refresh()
        #
        # # Check number of imgs in lone_char_container:
        # lone_container_imgs = s.find_elements_by_xpath("//*[@id='lone_char_container']/a")
        # self.assertEqual(len(lone_container_imgs), 0)
        #
        # # Check number of imgs in top_char_container:
        # top_container_imgs = s.find_elements_by_xpath("//*[@id='top_char_container']/a")
        # self.assertEqual(len(top_container_imgs), 65)
        #
        # # Check number of imgs in side_char_container:
        # side_container_imgs = s.find_elements_by_xpath("//*[@id='side_char_container']/a")
        # self.assertEqual(len(side_container_imgs), 0)

    def test_char_overlay_toggle_elite_smash(self):
        """ If a character image is clicked, its elite smash status is toggled, and the image is displayed
            in full colour/greyscale, depending on elite smash status."""
        s = self.selenium
        server_url = self.live_server_url
        game = self.game

        # Create characters:
        chars = create_characters(game, 5)
        first_char = chars[0]

        # Login and nav to char overlay page:
        login(s, server_url, self.user.username)
        s.get(server_url + reverse('mentor:char_overlay', args=[game.id]))

        # Note: Since character has just been created, no UserCharacter record will exist for this user and char.
        # Check that first character image is greyscale, since not in elite smash by default:
        first_char_imgs = s.find_elements_by_css_selector("img#" + snakify(first_char.name) + ".grayscale")
        self.assertEqual(len(first_char_imgs), 1)

        # Check that no colour img for first character exists (no grayscale CSS class):
        first_char_coloured = s.find_elements_by_css_selector("img#" + snakify(first_char.name) + ":not(.grayscale)")
        self.assertEqual(len(first_char_coloured), 0)

        # Click img:
        first_char_imgs[0].click()

        # Wait for page to refresh:
        time.sleep(0.5)

        # Test that character is full colour after reload:
        first_char_imgs = s.find_elements_by_css_selector("img#" + snakify(first_char.name) + ":not(.grayscale)")
        self.assertEqual(len(first_char_imgs), 1)

        # Click img again to toggle to true:
        first_char_imgs[0].click()
        time.sleep(0.5)

        # Check for grayscale after reload:
        first_char_imgs = s.find_elements_by_css_selector("img#" + snakify(first_char.name) + ".grayscale")
        self.assertEqual(len(first_char_imgs), 1)

    def test_elite_smash_status_persistence(self):
        """The elite smash status of all characters are kept after leaving the page and returning."""
        s = self.selenium
        game = self.game
        login(s, self.live_server_url, self.user.username)

        chars = create_characters(game, 5)
        s.get(self.live_server_url + reverse('mentor:char_overlay', args=[game.id]))

        s.find_element_by_id(snakify(chars[0].name)).click()
        time.sleep(0.2)
        s.find_element_by_id(snakify(chars[2].name)).click()
        time.sleep(0.2)
        s.find_element_by_id(snakify(chars[3].name)).click()
        time.sleep(0.5)

        # Check that clicked character imgs are not grayscale:
        char_imgs = s.find_elements_by_css_selector("img#" + snakify(chars[0].name) + ":not(.grayscale)")
        self.assertEqual(len(char_imgs), 1)
        char_imgs = s.find_elements_by_css_selector("img#" + snakify(chars[2].name) + ":not(.grayscale)")
        self.assertEqual(len(char_imgs), 1)
        char_imgs = s.find_elements_by_css_selector("img#" + snakify(chars[3].name) + ":not(.grayscale)")
        self.assertEqual(len(char_imgs), 1)

        s.get(self.live_server_url + reverse('mentor:index'))
        s.get(self.live_server_url + reverse('mentor:char_overlay', args=[game.id]))

        # Check that clicked character imgs are not grayscale:
        char_imgs = s.find_elements_by_css_selector("img#" + snakify(chars[0].name) + ":not(.grayscale)")
        self.assertEqual(len(char_imgs), 1)
        char_imgs = s.find_elements_by_css_selector("img#" + snakify(chars[2].name) + ":not(.grayscale)")
        self.assertEqual(len(char_imgs), 1)
        char_imgs = s.find_elements_by_css_selector("img#" + snakify(chars[3].name) + ":not(.grayscale)")
        self.assertEqual(len(char_imgs), 1)

    def test_chroma_key_toggle(self):
        """ The chroma key background can be toggled using the checkbox, and this preference persists
            after leaving the page."""
        s = self.selenium
        game = self.game
        login(s, self.live_server_url, self.user.username)

        chars = create_characters(game, 5)
        s.get(self.live_server_url + reverse('mentor:char_overlay', args=[game.id]))

        # Check that body background colour isn't chroma key:
        self.assertEqual(len(s.find_elements_by_css_selector('body.chromakey')), 0)

        # Click checkbox and check if body is now chromakey:
        s.find_element_by_id('chroma_checkbox').click()
        self.assertEqual(len(s.find_elements_by_css_selector('body.chromakey')), 1)

        # Navigate away from character overlay page and back again:
        s.get(self.live_server_url + reverse('mentor:index'))
        s.get(self.live_server_url + reverse('mentor:char_overlay', args=[game.id]))

        # Check that background is still chroma key:
        self.assertEqual(len(s.find_elements_by_css_selector('body.chromakey')), 1)

        # Toggle again to not chroma key and check:
        s.find_element_by_id('chroma_checkbox').click()
        self.assertEqual(len(s.find_elements_by_css_selector('body.chromakey')), 0)
