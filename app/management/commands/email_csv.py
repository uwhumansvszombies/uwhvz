from django.core.management.base import BaseCommand

#from app.models import most_recent_game
from app.util import get_game_participants, most_recent_game


class Command(BaseCommand):
    help = 'Prints a csv style sheet of participants in this game'

    def handle(self, *args, **options):
        game = most_recent_game()
        participants = get_game_participants(game)
        for p in participants:
            print(", ".join((p.user.email,p.user.first_name,p.user.last_name)))
