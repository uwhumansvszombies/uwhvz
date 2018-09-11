from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test, REDIRECT_FIELD_NAME
from django.http import Http404
from django.shortcuts import render
from django.utils import dateformat
from django.views import View

from app.models import Game


def player_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    def _is_player(user):
        game = most_recent_game()
        return user.is_authenticated and user.participant(game).type == 'Player'

    actual_decorator = user_passes_test(_is_player, login_url=login_url, redirect_field_name=redirect_field_name)
    if function:
        return actual_decorator(function)
    return actual_decorator


def moderator_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    def _is_moderator(user):
        game = most_recent_game()
        return user.is_authenticated and user.participant(game).type == 'Moderator'

    actual_decorator = user_passes_test(_is_moderator, login_url=login_url, redirect_field_name=redirect_field_name)
    if function:
        return actual_decorator(function)
    return actual_decorator


def volunteer_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    def _is_volunteer(user):
        return user.is_authenticated and user.is_volunteer

    actual_decorator = user_passes_test(_is_volunteer, login_url=login_url, redirect_field_name=redirect_field_name)
    if function:
        return actual_decorator(function)
    return actual_decorator


def game_exists() -> bool:
    return Game.objects.exists()


def most_recent_game() -> Game:
    return Game.objects.all().order_by('-created_at').first()


def game_required(function=None):
    def wrap(request, *args, **kwargs):
        if game_exists():
            return function(request, *args, **kwargs)
        else:
            raise Http404

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def active_game_required(function):
    def wrap(request, *args, **kwargs):
        if game_exists() and most_recent_game().is_active:
            return function(request, *args, **kwargs)
        else:
            raise Http404

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def running_game_required(function=None):
    def wrap(request, *args, **kwargs):
        if game_exists() and most_recent_game().is_running:
            return function(request, *args, **kwargs)
        else:
            raise Http404

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def normalize_email(email) -> str:
    """
    Normalize the email address by making the domain part of it lowercase.
    """
    email = email or ''
    try:
        email_name, domain_part = email.strip().rsplit('@', 1)
    except ValueError:
        pass
    else:
        email = email_name + '@' + domain_part.lower()
    return email


def format_datetime(value) -> datetime:
    return dateformat.format(value, settings.DATETIME_FORMAT)


class MobileSupportedView(View):
    desktop_template = "You did not supply a desktop template."
    mobile_template = "You did not supply a mobile template."

    def get(self, request):
        return self.mobile_or_desktop(request)

    def mobile_or_desktop(self, request, context=None):
        if request.user_agent.is_mobile:
            return render(request, self.mobile_template, context)
        else:
            return render(request, self.desktop_template, context)
