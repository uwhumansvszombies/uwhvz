from django.core.management.base import BaseCommand

from app.models import Player


class Command(BaseCommand):
    help = 'Prints a list of all emails'

    def handle(self, *args, **options):
        players = Player.objects.filter(active=True).all()
        player_emails = [p.user.email for p in players]
        print(", ".join(player_emails))
