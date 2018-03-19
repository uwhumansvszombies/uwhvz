from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from app.models import Game, Player, Tag, User, PlayerRole, SignupLocation


class PlayerValueTest(TestCase):
    def setUp(self):
        game = Game.objects.create_game(name='Test Game 2018')
        tiff = User.objects.create_user(username='tiff', email='tiff@email.com')
        tris = User.objects.create_user(username='tris', email='tris@email.com')
        signup_location = SignupLocation.objects.create_signup_location('SLC')
        self.tiff = Player.objects.create_player(tiff, game, PlayerRole.HUMAN, signup_location)
        self.tris = Player.objects.create_player(tris, game, PlayerRole.ZOMBIE, signup_location)

    def test_no_tags(self):
        self.assertEqual(self.tris.value(timezone.now()), 5)

    def test_one_tag(self):
        now = timezone.now()
        Tag.objects.create(initiator=self.tiff, receiver=(self.tris),
                           tagged_at=now - timedelta(seconds=1))
        self.assertEqual(self.tris.value(now - timedelta(hours=1)), 5)
        self.assertEqual(self.tris.value(now + timedelta(hours=1)), 4)
        self.assertEqual(self.tris.value(now), 4)

    def test_multiple_tags(self):
        now = timezone.now()
        for i in range(0, 3):
            Tag.objects.create(initiator=self.tiff, receiver=self.tris,
                               tagged_at=now - timedelta(hours=3 - i))
        self.assertEqual(self.tris.value(now), 2)

    def test_six_tags(self):
        now = timezone.now()
        for i in range(0, 6):
            Tag.objects.create(initiator=self.tiff, receiver=self.tris,
                               tagged_at=now - timedelta(hours=6 - i))
        self.assertEqual(self.tris.value(now), 0)

    def test_expired_tag(self):
        now = timezone.now()
        too_long_ago = now - timedelta(hours=9)
        Tag.objects.create(initiator=self.tiff, receiver=self.tris,
                           tagged_at=too_long_ago)
        self.assertEqual(self.tris.value(now), 5)
        Tag.objects.create(initiator=self.tiff, receiver=self.tris,
                           tagged_at=now - timedelta(seconds=1))
        self.assertEqual(self.tris.value(now), 4)


class PlayerScoreTest(TestCase):
    def setUp(self):
        game = Game.objects.create_game(name='Test Game 2018')
        tiff = User.objects.create_user(username='tiff', email='tiff@email.com')
        tris = User.objects.create_user(username='tris', email='tris@email.com')
        signup_location = SignupLocation.objects.create_signup_location('SLC')
        self.tiff = Player.objects.create_player(tiff, game, PlayerRole.HUMAN, signup_location)
        self.tris = Player.objects.create_player(tris, game, PlayerRole.ZOMBIE, signup_location)

    def test_no_tags(self):
        self.assertEqual(self.tiff.score(), 0)

    def test_one_tag(self):
        now = timezone.now()
        Tag.objects.create(initiator=self.tiff, receiver=self.tris, tagged_at=now)
        self.assertEqual(self.tiff.score(), 5)

    def test_multiple_tags(self):
        now = timezone.now()
        for i in range(0, 3):
            Tag.objects.create(initiator=self.tiff, receiver=self.tris,
                               tagged_at=now - timedelta(hours=3 - i))
        self.assertEqual(self.tiff.score(), 5 + 4 + 3)
