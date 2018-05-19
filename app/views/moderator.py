from django.contrib import messages
from django.shortcuts import render

from app.mail import send_signup_email
from app.models import Player, SignupLocation, Game
from app.util import moderator_required, require_post_parameters


@moderator_required
def player_list(request):
    players = Player.objects.all()
    return render(request, 'dashboard/player_list.html', {'players': players})


@moderator_required
def add_player(request):
    if request.method == 'POST':
        game_id, location_id, email = require_post_parameters(request, 'game', 'signup_location', 'email')
        location = SignupLocation.objects.get(pk=location_id)
        game = Game.objects.get(pk=game_id)
        send_signup_email(request, game, location, email)
        messages.add_message(request, messages.SUCCESS, f'Sent an email to: {email}!!')

    locations = SignupLocation.objects.all()
    games = Game.objects.all()
    return render(request, 'dashboard/add_player.html', {'signup_locations': locations, 'games': games})


@moderator_required
def signup_locations(request):
    locations = SignupLocation.objects.all()
    return render(request, 'dashboard/signup_locations.html', {'signup_locations': locations})
