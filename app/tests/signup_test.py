from django.test import Client
from django.test import TestCase

from app.models import SignupLocation, SignupToken, User, Game


class SignupTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('superuser@email.com', 'password')
        self.signup_location = SignupLocation.objects.create_signup_location('In a Test')
        self.game = Game.objects.create_game('Test Game')
        self.client = Client()
        self.client.login(username='superuser@email.com', password='password')

    def test_signup_token_creation(self):
        test_email = 'email@test.com'
        self.client.post('/dashboard/add_player',
                         {'game': self.game, 'email': test_email, 'signup_location': 'In a Test'})
        signup_token = SignupToken.objects.all().first()
        self.assertEqual(signup_token.email, test_email)
        self.assertEqual(signup_token.signup_location, self.signup_location)
