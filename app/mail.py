from django.conf import settings
from django.template.loader import render_to_string
from post_office import mail


def _send_mail_template(request, plaintext_template, html_template, subject, recipient, context=None):
    msg_plain = render_to_string(plaintext_template, context, request)
    msg_html = render_to_string(html_template, context, request)
    mail.send(
        recipients=[recipient],
        sender=settings.DEFAULT_FROM_EMAIL,
        subject=subject,
        message=msg_plain,
        html_message=msg_html
    )


def send_signup_email(request, signup_invite, game):
    _send_mail_template(
        request,
        "email/signup.txt",
        "email/signup.html",
        "Welcome to HvZ",
        signup_invite.email,
        {'signup_invite': signup_invite, 'game': game, 'contact_email': settings.DEFAULT_FROM_EMAIL}
    )


def send_signup_reminder(request, email, url, game):
    _send_mail_template(
        request,
        "email/signup_reminder.txt",
        "email/signup_reminder.html",
        "[ACTION REQUIRED] UW HvZ - Uncompleted Game Signup",
        email,
        {'signup_url': url, 'game': game},
    )


def send_stun_email(request, tag):
    _send_mail_template(
        request,
        "email/stun.txt",
        "email/stun.html",
        "You've Been Stunned",
        tag.receiver.user.email,
        {'tag': tag}
    )


def send_tag_email(request, tag):
    _send_mail_template(
        request,
        "email/tag.txt",
        "email/tag.html",
        "You've Been Tagged",
        tag.receiver.user.email,
        {'tag': tag}
    )
