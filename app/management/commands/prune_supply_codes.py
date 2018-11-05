from django.core.management.base import BaseCommand

from app.models import SupplyCode
from app.util import most_recent_game


class Command(BaseCommand):
    help = 'Marks all unclaimed supply codes as inactive'

    def handle(self, *args, **options):
        game = most_recent_game()
        unclaimed_codes = SupplyCode.objects.filter(game=game, claimed_by__isnull=True)
        for code in unclaimed_codes:
            code.active = False
            code.save()
