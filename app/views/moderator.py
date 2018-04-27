from django.shortcuts import render

from app.models import Player, SignupLocation, SignupToken, Game
from app.util import moderator_required, send_mail_template, check_argument


@moderator_required
def player_list(request):
    players = Player.objects.all()
    return render(request, 'dashboard/player_list.html', {'players': players})


@moderator_required
def add_player(request):
    if request.method == 'POST':
        _game = request.POST.get('game')
        _location = request.POST.get('signup_location')
        email = request.POST.get('email')
        check_argument(request, _game, 'Game cannot be blank.')
        check_argument(request, _location, 'Signup location cannot be blank.')
        check_argument(request, email, 'Email cannot be blank.')

        location = SignupLocation.objects.get(location=_location)
        game = Game.objects.get(name=_game)
        signup_token = SignupToken.objects.create_signup_token(game, location, email)
        send_mail_template(
            request,
            'email/signup.txt',
            'email/signup.html',
            'Welcome to HvZ',
            email,
            {'signup_token': signup_token}
        )

    locations = SignupLocation.objects.all()
    games = Game.objects.all()
    return render(request, 'dashboard/add_player.html', {'signup_locations': locations, 'games': games})


@moderator_required
def signup_locations(request):
    locations = SignupLocation.objects.all()
    return render(request, 'dashboard/signup_locations.html', {'signup_locations': locations})
