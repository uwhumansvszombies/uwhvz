from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Player, SignupLocation
from .util import moderator_required


def index(request):
    return render(request, 'index.html')


@login_required
def dashboard(request):
    return render(request, 'dashboard/index.html')


@login_required
def report_tag(request):
    if request.method == 'POST':
        # Find the player using the code from the request
        # Do the tag using TagManager
        # Report any errors if there are any
        messages.add_message(request, messages.ERROR, "There was an error reporting a tag:")
        # Report success if it worked!
    return render(request, 'dashboard/index.html')


@moderator_required
def player_list(request):
    players = Player.objects.all()
    return render(request, 'dashboard/player_list.html', {'players': players})


@moderator_required
def add_player(request):
    if request.method == 'POST':
        print("post!!!")
    return render(request, 'dashboard/add_player.html')


@moderator_required
def signup_locations(request):
    locations = SignupLocation.objects.all()
    return render(request, 'dashboard/signup_locations.html', {'signup_locations': locations})
