from django.core.management.base import BaseCommand

from app.models import Player, PlayerRole


class Command(BaseCommand):
    help = 'Prints a list of all zombie emails'

    def handle(self, *args, **options):
        players = Player.objects.filter(active=True, role=PlayerRole.ZOMBIE).all()
        player_emails = [p.user.email for p in players]
        print(", ".join(player_emails))
