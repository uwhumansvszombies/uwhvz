from django.core.management.base import BaseCommand
from django.urls import reverse

from app.mail import send_signup_reminder
from app.models import SignupInvite


class Command(BaseCommand):
    help = 'Sends email reminders to unused signup tokens.'

    def handle(self, *args, **options):
        unused_tokens = SignupInvite.objects.filter(used_at__isnull=True)
        for token in unused_tokens:
            path = reverse('signup', args=[token.id])
            url = f'https://uwhvz.uwaterloo.ca{path}'
            send_signup_reminder(None, token.email, url)
