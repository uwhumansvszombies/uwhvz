from django.core.management.base import BaseCommand

from app.models import Player, most_recent_game


class Command(BaseCommand):
    help = 'Prints a list of all emails'

    def handle(self, *args, **options):
        game = most_recent_game()
        players = Player.objects.filter(game=game, active=True)
        player_emails = [p.user.email for p in players]
        print(", ".join(player_emails))
