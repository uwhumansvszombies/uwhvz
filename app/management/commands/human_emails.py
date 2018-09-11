from django.core.management.base import BaseCommand

from app.models import Player, PlayerRole, Spectator, Moderator, most_recent_game


class Command(BaseCommand):
    help = 'Prints a list of all human emails'

    def handle(self, *args, **options):
        game = most_recent_game()
        spectators = Spectator.objects.filter(game=game)
        moderators = Moderator.objects.filter(game=game)
        humans = Player.objects.filter(game=game, active=True, role=PlayerRole.HUMAN)

        spectator_emails = [p.user.email for p in spectators]
        moderator_emails = [p.user.email for p in moderators]
        human_emails = [p.user.email for p in humans] + spectator_emails + moderator_emails
        print(", ".join(human_emails))
