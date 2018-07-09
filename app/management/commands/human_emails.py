from django.core.management.base import BaseCommand

from app.models import Player, PlayerRole


class Command(BaseCommand):
    help = 'Prints a list of all human emails'

    def handle(self, *args, **options):
        players = Player.objects.filter(active=True, role=PlayerRole.HUMAN).all()
        player_emails = [p.user.email for p in players]
        print(", ".join(player_emails))
