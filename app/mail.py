from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import Template
from django.template.loader import render_to_string
from jinja2 import Environment, BaseLoader

from app.models import Email
from app.util import most_recent_game


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

def _dynamic_send_mail_template(request, email_object, subject, recipient, context=None):
    body_temp = Template(email_object.data)
    body = body_temp.render(context, request)
    msg = EmailMultiAlternatives(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[],
                bcc=[recipient]
            )
    msg.content_subtype = "html"
    try:
        return msg.send()
    except:
        print("An Error Occurred in Dynamic Email Send Code")


def send_signup_email(request, signup_invite, game):
    # _dynamic_send_mail_template(
    #     request,
    #     Email.objects.get(name="Signup Email (Visible only to Mods) - sent to players",game=game),
    #     "Welcome to HvZ!",
    #     signup_invite.email,
    #     {'signup_invite': signup_invite}
    # )
    
    _send_mail_template(
       request,
       "email/signup.txt",
       "email/signup.html",
       "Welcome to HvZ",
       signup_invite.email,
       {'signup_invite': signup_invite, 'game': game}
    )


def send_signup_reminder(request, signup_invite, game):
    _dynamic_send_mail_template(
        request,
        Email.objects.get(name="Signup Reminder Email (Visible only to Mods) - sent to players",game=most_recent_game()),
        "[ACTION REQUIRED] UW HvZ - Uncompleted Game Signup",
        signup_invite.email,
        {'signup_invite': signup_invite, 'game': game}
    )
    
    #_send_mail_template(
    #    request,
    #    "email/signup_reminder.txt",
    #    "email/signup_reminder.html",
    #    "[ACTION REQUIRED] UW HvZ - Uncompleted Game Signup",
    #    signup_invite.email,
    #    {'signup_invite': signup_invite, 'game': game}
    #)
    
def send_start_email(request, participant, game):
    _dynamic_send_mail_template(
        request,
        Email.objects.get(name="Game Start Email (Visible only to Mods) - sent to players",game=most_recent_game()),
        "UW HvZ - Game Start!",
        participant.user.email,
        {'participant': participant, 'game': game}
    )
    
    #_send_mail_template(
    #    request,
    #    "email/game_start.txt",
    #    "email/game_start.html",
    #    "UW HvZ - Game Start!",
    #    participant.user.email,
    #    {'participant': participant, 'game': game},
    #)


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
