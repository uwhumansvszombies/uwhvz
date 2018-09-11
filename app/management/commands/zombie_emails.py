from django.core.management.base import BaseCommand

from app.models import Player, PlayerRole, Spectator, Moderator, most_recent_game


class Command(BaseCommand):
    help = 'Prints a list of all zombie emails'

    def handle(self, *args, **options):
        game = most_recent_game()
        spectators = Spectator.objects.filter(game=game)
        moderators = Moderator.objects.filter(game=game)
        zombies = Player.objects.filter(game=game, active=True, role=PlayerRole.ZOMBIE)

        spectator_emails = [p.user.email for p in spectators]
        moderator_emails = [p.user.email for p in moderators]
        zombie_emails = [p.user.email for p in zombies] + spectator_emails + moderator_emails
        print(", ".join(zombie_emails))
