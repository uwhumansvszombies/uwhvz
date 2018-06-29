import random

from django.core.management.base import BaseCommand

from app.models import User, Game, Player, PlayerRole, SignupLocation

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

        roles = [PlayerRole.HUMAN, PlayerRole.ZOMBIE, PlayerRole.SPECTATOR]

        SignupLocation.objects.create_signup_location('SLC')
        SignupLocation.objects.create_signup_location('Online')
        SignupLocation.objects.create_signup_location('EIT')
        SignupLocation.objects.create_signup_location('DC')

        users = []
        for name in names:
            first, last = name.split(' ')
            user = User.objects.create_user(f'{first.lower()}@email.com', 'password', first_name=first, last_name=last)
            users.append(user)

        game = Game.objects.create_game('Spring 2018')
        Player.objects.create_player(root, game, PlayerRole.SPECTATOR)

        for i in range(0, 50):
            Player.objects.create_player(users[i], game, random.choice(roles))
