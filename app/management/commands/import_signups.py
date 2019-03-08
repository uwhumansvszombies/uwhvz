import codecs
import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from app.mail import send_signup_email
from app.models import most_recent_game, SignupInvite, SignupLocation
from app.models.util import normalize_email


class Command(BaseCommand):
    help = 'Adds users from a CSV with format: email, signup location.'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help="file path")

    def handle(self, *args, **options):
        path = Path(options['path'])

        if not path.exists():
            raise ValueError(f'The path {path} does not exist.')
        game = most_recent_game()
        locations = SignupLocation.objects.filter(game=game)

        with open(path, 'rb') as csv_file:
            reader = csv.DictReader(codecs.iterdecode(csv_file, 'utf-8'), ['email', 'location'])
            for row in reader:
                try:
                    self.process_row(row, game, locations)
                except Exception as e:
                    print(f'Error: {e}')

    @staticmethod
    def process_row(row, game, locations):
        csv_email = normalize_email(str(row['email']).strip())
        csv_location = str(row['location']).strip()
        if SignupInvite.objects.filter(game=game, email=csv_email).count() > 0:
            print(f'Skipping {csv_email} because the user is already registered for the game.')
            return
        location = locations.get(name=csv_location)
        signup_invite = SignupInvite.objects.create_signup_invite(game, location, csv_email)
        send_signup_email(None, signup_invite, game)
        print(f"Sent a signup email to {csv_email}.")
