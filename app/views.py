from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from .models import Player, SignupLocation
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


@user_passes_test(is_moderator)
def add_player(request):
    if request.method == 'POST':
        print("post!!!")
    return render(request, 'moderator/add_player.html')


@user_passes_test(is_moderator)
def signup_locations(request):
    locations = SignupLocation.objects.all()
    return render(request, 'moderator/signup_locations.html', {'signup_locations': locations})
