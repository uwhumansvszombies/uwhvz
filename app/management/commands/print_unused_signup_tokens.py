from django.core.management.base import BaseCommand

from app.models import SignupInvite


class Command(BaseCommand):
    help = 'Prints a comma delimited list of emails who haven\'t created an account yet.'

    def handle(self, *args, **options):
        unused = list(SignupInvite.objects.filter(used_at__isnull=True).values_list('email', flat=True).distinct())
        print(", ".join(unused))
