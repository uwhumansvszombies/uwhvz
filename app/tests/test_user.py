from django.test import TestCase

from app.models import Game
from app.tests.user_tester import UserTester


class UserTest(TestCase):
    def setUp(self):
        self.user_tester = UserTester()
        self.game = Game.objects.get(name='Test Game')
        self.user, self.player = self.user_tester.create_user_and_player('tiff@email.com', 'first', 'last')

    def test_one_user_per_email(self):
        with self.assertRaises(AttributeError):
            self.user, self.player = self.user_tester.create_user_and_player('tiff@email.com', 'first', 'last')
