from django.core.management import call_command
from django.test import TestCase

from app.models import Player


class SeedDataTest(TestCase):
    def test_that_it_runs_without_error(self):
        call_command('seed_data')
        self.assertEqual(Player.objects.all().count(), 54)
