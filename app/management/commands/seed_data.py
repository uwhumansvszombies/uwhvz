import random

from django.core.management.base import BaseCommand

from app.models import User, Game, Player, PlayerRole, SignupLocation, Spectator, Moderator, ParticipantRole

names = ['Eliseo Perlman',
         'Hettie Pugsley',
         'Else Vartanian',
         'Corinna Slover',
         'Vannessa Stultz',
         'Dion Demott',
         'Riva Shock',
         'Charita Ralphs',
         'Lillie Wannamaker',
         'Soila Brasher',
         'Truman Degraffenreid',
         'Verona Broady',
         'Larae Coker',
         'Ernesto Mortensen',
         'Tyesha Worden',
         'Shondra Bondy',
         'Britney Mirabella',
         'Shera Klimas',
         'Amada Milano',
         'Emerson Buffington',
         'Hiroko Bailer',
         'Deeann Maher',
         'Glen Creagh',
         'Kurt Preble',
         'Glenna Ringo',
         'Debbie Frisby',
         'Maximina Yamashita',
         'Georgann Alsop',
         'Jayme Hilley',
         'Rachell Kempton',
         'Estela Wilcoxon',
         'Anton Spafford',
         'Gale Legette',
         'Tanesha Mcsorley',
         'Kary Schmieder',
         'Zaida Nyland',
         'Arron Romberger',
         'Evangeline Dagenhart',
         'Cindy Sandor',
         'Valencia Paschall',
         'Sommer Thomsen',
         'Vikki Meunier',
         'September Froelich',
         'Lawanda Villanveva',
         'Cordie Jaimes',
         'Orval Cude',
         'Hans Buelow',
         'Greta Heaps',
         'Vernell Kerschner',
         'Tory Shulman']


class Command(BaseCommand):
    help = 'Generates seed data'

    def handle(self, *args, **options):
        if User.objects.filter(email='root').exists():
            return

        root = User.objects.create_superuser('root', 'toor', first_name='Super', last_name='User')
        game = Game.objects.create_game('Spring 2018')

        SignupLocation.objects.create_signup_location('SLC', game=game)
        SignupLocation.objects.create_signup_location('Online', game=game)
        SignupLocation.objects.create_signup_location('EIT', game=game)
        SignupLocation.objects.create_signup_location('DC', game=game)

        users = []
        for name in names:
            first, last = name.split(' ')
            user = User.objects.create_user(f'{first.lower()}@email.com', 'password', first_name=first, last_name=last)
            users.append(user)

        Moderator.objects.create_moderator(root, game)

        roles = [PlayerRole.HUMAN, PlayerRole.ZOMBIE, ParticipantRole.MODERATOR, ParticipantRole.SPECTATOR]
        for i in range(0, 50):
            role = random.choice(roles)
            if role == ParticipantRole.MODERATOR:
                Moderator.objects.create_moderator(user=users[i], game=game)
            elif role == ParticipantRole.SPECTATOR:
                Spectator.objects.create_spectator(user=users[i], game=game)
            else:
                Player.objects.create_player(user=users[i], game=game, role=role)

        zombie = User.objects.create_user('zombie@email.com', 'password', first_name='Zombie', last_name='Player')
        human = User.objects.create_user('human@email.com', 'password', first_name='Human', last_name='Player')
        spectator = User.objects.create_user('spectator@email.com', 'password', first_name='A', last_name='Spectator')

        Player.objects.create_player(zombie, game, PlayerRole.ZOMBIE)
        Player.objects.create_player(human, game, PlayerRole.HUMAN)
        Spectator.objects.create_spectator(spectator, game)
