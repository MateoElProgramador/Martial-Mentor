from django.urls import reverse
from selenium import webdriver
import chromedriver_binary  # adds chromedriver binary to path

from mentor.tests.helpers import MyStaticLiveServerTestCase, create_user, login


class RegistrationTests(MyStaticLiveServerTestCase):

    def sign_up(self, username, email, password):
        """Helper method just for registration tests, to enter signup fields with given arguments."""
        s = self.selenium
        s.get(self.live_server_url + reverse('mentor:signup'))
        s.find_element_by_name('username').send_keys(username)
        s.find_element_by_name('email').send_keys(email)
        s.find_element_by_name('password1').send_keys(password)
        s.find_element_by_name('password2').send_keys(password)
        s.find_element_by_xpath('//input[@value="Sign up"]').click()

    def test_valid_signup(self):
        """The user is able to create an account by signing up."""
        s = self.selenium
        self.sign_up('Dabuz', 'dabuz@thinkpad.gg', 'IceCreamIsTheBest')

        # Successful signup redirects to login page:
        assert 'login' in s.current_url

    def test_invalid_signup(self):
        """ If invalid values are entered for signup form fields, the user is redirected back to the signup page and
            errors are displayed."""
        s = self.selenium

        # Create a user with username Clarence:
        create_user('Clarence')

        # Username blank:
        self.sign_up('', 'yes@no.maybe', 'ExcellentPassword')
        # (Don't know how to test for JavaScript validation messages, this is default HTML behaviour anyway)
        assert 'signup' in s.current_url

        # Existing username:
        self.sign_up('Clarence', 'yes@no.maybe', 'ExcellentPassword')
        assert 'A user with that username already exists.' in s.page_source

        # Blank email:
        self.sign_up('Eustace', '', 'ExquisitePassword')
        assert 'signup' in s.current_url

        # Invalid email:
        self.sign_up('Eustace', 'thisaintan@email', 'ExquisitePassword')
        assert 'signup' in s.current_url

        # Blank password:
        self.sign_up('Eustace', 'yep@g.com', '')
        assert 'signup' in s.current_url

        # Password too short:
        self.sign_up('Eustace', 'yep@g.com', 'ttt')
        assert 'This password is too short. It must contain at least 8 characters.' in s.page_source

        # Password entirely numeric:
        self.sign_up('Eustace', 'yep@g.com', '888888888')
        assert 'This password is entirely numeric.' in s.page_source

    def test_valid_login(self):
        """If existing, valid user details are entered on the login page, the user is logged in."""
        s = self.selenium
        create_user('LegitLarry', password='PurePassword')
        login(s, self.live_server_url, 'LegitLarry', 'PurePassword')
        self.assertEqual(s.current_url, self.live_server_url + reverse('mentor:index'))

    def test_invalid_login(self):
        """If an incorrect username or password is entered, the user will not be logged in."""
        s = self.selenium
        create_user('LawfulLaurence', password='NoSlacking')

        # Incorrect password:
        login(s, self.live_server_url, 'LawfulLaurence', 'IncorrectPasswordOops')
        assert 'Please enter a correct username and password.' in s.page_source

        # Non-existent username:
        login(s, self.live_server_url, 'UnlawfulUrsula', 'IncorrectPasswordOops')
        assert 'Please enter a correct username and password.' in s.page_source
