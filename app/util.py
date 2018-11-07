from datetime import datetime
from functools import wraps

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test, REDIRECT_FIELD_NAME
from django.http import Http404
from django.shortcuts import render
from django.utils import dateformat
from django.views import View
from queryset_sequence import QuerySetSequence

from app.models import Game, Player, Moderator, Spectator


def player_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    def _is_player(user):
        game = most_recent_game()
        return user.is_authenticated and user.participant(game) and user.participant(game).is_player

    actual_decorator = user_passes_test(_is_player, login_url=login_url, redirect_field_name=redirect_field_name)
    if function:
        return actual_decorator(function)
    return actual_decorator


def moderator_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    def _is_moderator(user):
        game = most_recent_game()
        return user.is_authenticated and (user.participant(game) and user.participant(game).is_moderator or user.is_staff)

    actual_decorator = user_passes_test(_is_moderator, login_url=login_url, redirect_field_name=redirect_field_name)
    if function:
        return actual_decorator(function)
    return actual_decorator


def volunteer_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    def _is_volunteer(user):
        return user.is_authenticated and (user.is_volunteer or user.is_staff)

    actual_decorator = user_passes_test(_is_volunteer, login_url=login_url, redirect_field_name=redirect_field_name)
    if function:
        return actual_decorator(function)
    return actual_decorator


def game_exists() -> bool:
    return Game.objects.exists()


def most_recent_game() -> Game:
    return Game.objects.all().order_by('-created_at').first()


def get_game_participants(game: Game, queryset_required: bool = False):
    players = Player.objects.filter(game=game, active=True)
    mods = Moderator.objects.filter(game=game, active=True)
    spectators = Spectator.objects.filter(game=game, active=True)

    return QuerySetSequence(players, mods, spectators)


def game_required(function=None):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if game_exists():
            pass
        else:
            raise Http404()
        return function(request, *args, **kwargs)

    return wrap


def signups_game_required(function=None):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if game_exists() and most_recent_game().is_signups:
            pass
        else:
            raise Http404()
        return function(request, *args, **kwargs)

    return wrap


def running_game_required(function=None):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if game_exists() and most_recent_game().is_running:
            pass
        else:
            raise Http404()
        return function(request, *args, **kwargs)

    return wrap


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
