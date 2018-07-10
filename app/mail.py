from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


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


def send_signup_email(request, signup_invite):
    _send_mail_template(
        request,
        'email/signup.txt',
        'email/signup.html',
        'Welcome to HvZ',
        signup_invite.email,
        {'signup_invite': signup_invite}
    )


def send_signup_reminder(request, email, url):
    _send_mail_template(
        request,
        'email/signup_reminder.txt',
        'email/signup_reminder.html',
        '[ACTION REQUIRED] UW Humans vs Zombies',
        email,
        {'signup_url': url}
    )


def send_stun_email(request, tag):
    _send_mail_template(
        request,
        'email/stun.txt',
        'email/stun.html',
        'You\'ve Been Stunned',
        tag.receiver.user.email,
        {'tag': tag}
    )


def send_tag_email(request, tag):
    _send_mail_template(
        request,
        'email/tag.txt',
        'email/tag.html',
        'You\'ve Been Tagged',
        tag.receiver.user.email,
        {'tag': tag}
    )
