from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, REDIRECT_FIELD_NAME
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import render
from django.views import View


def moderator_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    def _is_moderator(user):
        return user.is_authenticated and user.is_moderator

    actual_decorator = user_passes_test(_is_moderator, login_url=login_url, redirect_field_name=redirect_field_name)
    if function:
        return actual_decorator(function)
    return actual_decorator


def require_post_parameters(request, *parameters):
    params = []
    for p in parameters:
        param = request.POST.get(p)
        params.append(param)
        check_argument(request, param, f'{p} cannot be blank.')
    return params


def check_argument(request, predicate, message="Something went wrong", level=messages.ERROR):
    if not predicate:
        messages.add_message(request, level, message)
        # TODO: Does this fail nicely? Really all I want here is a way to return to
        # the current view with a message added. Perhaps a custom middleware to catch
        # some exception?
        raise SuspiciousOperation(message)


def normalize_email(email):
    """
    Normalize the email address by lowercasing the domain part of it.
    """
    email = email or ''
    try:
        email_name, domain_part = email.strip().rsplit('@', 1)
    except ValueError:
        pass
    else:
        email = email_name + '@' + domain_part.lower()
    return email


def site_url(request):
    return {'SITE_URL': settings.SITE_URL}


class MobileSupportedView(View):
    desktop_template = 'You did not supply a desktop template'
    mobile_template = 'You did not supply a mobile template'

    def get(self, request):
        return self.mobile_or_desktop(request)

    def mobile_or_desktop(self, request, context=None):
        if request.user_agent.is_mobile:
            return render(request, self.mobile_template, context)
        else:
            return render(request, self.desktop_template, context)