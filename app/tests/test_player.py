from django.test import TestCase

from app.models import Game, Player, PlayerRole
from app.tests.user_tester import UserTester


class PlayerTest(TestCase):
    def setUp(self):
        user_tester = UserTester()
        self.game = Game.objects.get(name='Test Game')
        self.user, self.player = user_tester.create_user_and_player('tiff@email.com', 'first', 'last')

    def test_one_active_player_per_game(self):
        with self.assertRaises(ValueError):
            Player.objects.create_player(self.user, self.game, PlayerRole.HUMAN)

    def test_killing(self):
        self.player.kill()
        self.assertEqual(self.user.player(self.game).role, PlayerRole.ZOMBIE)
