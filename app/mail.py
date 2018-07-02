from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from app.models import SignupInvite


def send_signup_email(request, game, location, email):
    signup_invite = SignupInvite.objects.create_signup_invite(game, location, email)
    _send_mail_template(
        request,
        'email/signup.txt',
        'email/signup.html',
        'Welcome to HvZ',
        email,
        {'signup_invite': signup_invite}
    )


def _send_mail_template(request, plaintext_template, html_template, subject, recipient, context=None):
    msg_plain = render_to_string(plaintext_template, context, request)
    msg_html = render_to_string(html_template, context, request)
    return send_mail(
        subject=subject,
        message=msg_plain,
        html_message=msg_html,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient]
    )
