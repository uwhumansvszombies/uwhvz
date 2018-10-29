from django.core.management.base import BaseCommand

from app.models import SupplyCode


class Command(BaseCommand):
    help = 'Marks all unclaimed supply codes as inactive'

    def handle(self, *args, **options):
        unclaimed_codes = SupplyCode.objects.filter(claimed_by__isnull=True)
        for code in unclaimed_codes:
            code.active = False
            code.save()
