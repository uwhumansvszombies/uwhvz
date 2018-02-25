from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from app.accounts import User
from app.models import Game, Player, Tag


class PlayerValueTest(TestCase):
    def setUp(self):
        game = Game.objects.create(name='Test Game 2018')
        tiff = User.objects.create_user(username='tiff')
        tris = User.objects.create_user(username='tris')
        Player.objects.create(user=tiff, game=game,
                              code='_TIFF_', role=Role.HUMAN)
        Player.objects.create(user=tris, game=game,
                              code='_TRIS_', role=Role.ZOMBIE)

    def test_no_tags(self):
        tris = User.objects.get(username='tris').player_set.all()[0]
        self.assertEqual(tris.value(timezone.now()), 5)

    def test_one_tag(self):
        tris = User.objects.get(username='tris').player_set.all()[0]
        tiff = User.objects.get(username='tiff').player_set.all()[0]
        now = timezone.now()
        Tag.objects.create(initiator=tiff, receiver=tris,
                           tagged_at=now - timedelta(seconds=1))
        self.assertEqual(tris.value(now - timedelta(hours=1)), 5)
        self.assertEqual(tris.value(now + timedelta(hours=1)), 4)
        self.assertEqual(tris.value(now), 4)

    def test_multiple_tags(self):
        tris = User.objects.get(username='tris').player_set.all()[0]
        tiff = User.objects.get(username='tiff').player_set.all()[0]
        now = timezone.now()
        for i in range(0, 3):
            Tag.objects.create(initiator=tiff, receiver=tris,
                               tagged_at=now - timedelta(hours=3 - i))
        self.assertEqual(tris.value(now), 2)

    def test_six_tags(self):
        tris = User.objects.get(username='tris').player_set.all()[0]
        tiff = User.objects.get(username='tiff').player_set.all()[0]
        now = timezone.now()
        for i in range(0, 6):
            Tag.objects.create(initiator=tiff, receiver=tris,
                               tagged_at=now - timedelta(hours=6 - i))
        self.assertEqual(tris.value(now), 0)

    def test_expired_tag(self):
        tris = User.objects.get(username='tris').player_set.all()[0]
        tiff = User.objects.get(username='tiff').player_set.all()[0]
        now = timezone.now()
        too_long_ago = now - timedelta(hours=9)
        Tag.objects.create(initiator=tiff, receiver=tris,
                           tagged_at=too_long_ago)
        self.assertEqual(tris.value(now), 5)
        Tag.objects.create(initiator=tiff, receiver=tris,
                           tagged_at=now - timedelta(seconds=1))
        self.assertEqual(tris.value(now), 4)


class PlayerScoreTest(TestCase):
    def setUp(self):
        game = Game.objects.create(name='Test Game 2018')
        tiff = User.objects.create_user(username='tiff')
        tris = User.objects.create_user(username='tris')
        Player.objects.create(user=tiff, game=game,
                              code='_TIFF_', role=Role.HUMAN)
        Player.objects.create(user=tris, game=game,
                              code='_TRIS_', role=Role.ZOMBIE)

    def test_no_tags(self):
        tiff = User.objects.get(username='tiff').player_set.all()[0]
        self.assertEqual(tiff.score(), 0)

    def test_one_tag(self):
        tris = User.objects.get(username='tris').player_set.all()[0]
        tiff = User.objects.get(username='tiff').player_set.all()[0]
        now = timezone.now()
        Tag.objects.create(initiator=tiff, receiver=tris, tagged_at=now)
        self.assertEqual(tiff.score(), 5)

    def test_multiple_tags(self):
        tris = User.objects.get(username='tris').player_set.all()[0]
        tiff = User.objects.get(username='tiff').player_set.all()[0]
        now = timezone.now()
        for i in range(0, 3):
            Tag.objects.create(initiator=tiff, receiver=tris,
                               tagged_at=now - timedelta(hours=3 - i))
        self.assertEqual(tiff.score(), 5 + 4 + 3)
