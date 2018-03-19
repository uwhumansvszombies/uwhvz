from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from .models import Player
from .util import is_moderator


def index(request):
    return render(request, 'index.html')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@user_passes_test(is_moderator)
def player_list(request):
    players = Player.objects.all()
    return render(request, 'moderator/player_list.html', {'players': players})
