from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, REDIRECT_FIELD_NAME
from django.core.exceptions import SuspiciousOperation
from django.core.mail import send_mail
from django.template.loader import render_to_string


def moderator_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    def _is_moderator(user):
        return user.is_authenticated and user.is_moderator()

    actual_decorator = user_passes_test(_is_moderator, login_url=login_url, redirect_field_name=redirect_field_name)
    if function:
        return actual_decorator(function)
    return actual_decorator


def send_mail_template(request, plaintext_template, html_template, subject, recipient, context=None):
    msg_plain = render_to_string(plaintext_template, context, request)
    msg_html = render_to_string(html_template, context, request)
    from_email = '???'
    return send_mail(
        subject=subject,
        message=msg_plain,
        html_message=msg_html,
        from_email=from_email,
        recipient_list=[recipient]
    )


def check_argument(request, predicate, message="Something went wrong", level=messages.ERROR):
    if not predicate:
        messages.add_message(request, level, message)
        # TODO: Does this fail nicely? Really all I want here is a way to return to
        # the current view with a message added. Perhaps a custom middleware to catch
        # some exception?
        raise SuspiciousOperation(message)


def site_url(request):
    return {'SITE_URL': settings.SITE_URL}
