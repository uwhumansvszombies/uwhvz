from django.core.management.base import BaseCommand

from app.models import most_recent_game
from app.util import get_game_participants


class Command(BaseCommand):
    help = 'Prints a list of all emails'

    def handle(self, *args, **options):
        game = most_recent_game()
        participants = get_game_participants(game)
        participant_emails = [p.user.email for p in participants]
        print(", ".join(participant_emails))
