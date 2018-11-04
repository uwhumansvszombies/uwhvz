from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from app.models import Game, PlayerRole
from app.tests.helpers.tag_tester import TagTester
from app.tests.helpers.user_tester import UserTester


class TagTest(TestCase):
    def setUp(self):
        user_tester = UserTester()
        self.game = Game.objects.get(name='Test Game')
        self.tag_tester = TagTester()
        self.human_user, self.human = user_tester.create_user_and_player('human@email.com', 'Human', 'Being')
        _, zombie = user_tester.create_user_and_player('zombie@email.com', 'Zombie', 'Undead')
        self.zombie = zombie.kill()
        self.game.started_on = timezone.now()
        self.game.save()

    def test_no_tags(self):
        self.assertEqual(self.zombie.value(timezone.now()), 5)
        self.assertEqual(self.human.score(), 0)

    def test_one_tag(self):
        now = timezone.now()
        self.tag_tester.tag(self.human, self.zombie, now - timedelta(seconds=1))
        self.assertEqual(self.zombie.value(now - timedelta(hours=1)), 5)
        self.assertEqual(self.zombie.value(now + timedelta(hours=1)), 4)
        self.assertEqual(self.zombie.value(now), 4)
        self.assertEqual(self.human.score(), 5)

    def test_multiple_tags(self):
        now = timezone.now()
        for i in range(0, 3):
            self.tag_tester.tag(self.human, self.zombie, now - timedelta(hours=3 - i))
        self.assertEqual(self.zombie.value(now), 2)
        self.assertEqual(self.human.score(), 5 + 4 + 3)

    def test_six_tags(self):
        now = timezone.now()
        for i in range(0, 6):
            self.tag_tester.tag(self.human, self.zombie, now - timedelta(hours=6 - i))
        self.assertEqual(self.zombie.value(now), 0)

    def test_expired_tag(self):
        now = timezone.now()
        too_long_ago = now - timedelta(hours=9)
        self.tag_tester.tag(self.human, self.zombie, too_long_ago)
        self.assertEqual(self.zombie.value(now), 5)
        self.tag_tester.tag(self.human, self.zombie, now - timedelta(seconds=1))
        self.assertEqual(self.zombie.value(now), 4)

    def test_that_humans_turn_into_zombies(self):
        self.tag_tester.tag(self.zombie, self.human, timezone.now())
        self.assertEqual(self.human_user.participant(self.game).role, PlayerRole.ZOMBIE)
