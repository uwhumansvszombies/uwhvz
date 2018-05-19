from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.utils import dateparse

from app.models import Player, Tag, Game
from app.util import require_post_parameters


def index(request):
    return render(request, 'index.html')


@login_required
def dashboard(request):
    try:
        player = request.user.player_set.get()
    except ObjectDoesNotExist:
        messages.add_message(request, messages.INFO, "You haven't signed up for any games yet.")
        return redirect('game_signup')
    team_score = sum([p.score() for p in Player.objects.all()])
    return render(request, 'dashboard/index.html', {'player': player, 'team_score': team_score})


@login_required
def report_tag(request):
    if request.method == 'POST':
        game_id, player_code, date, time, location, description = \
            require_post_parameters(request, 'game', 'player_code', 'date', 'time', 'location', 'description')
        game = Game.objects.get(pk=game_id)
        initiating_player = request.user.player(game)
        receiving_player = Player.objects.get(code=player_code)
        # TODO: Time zone?
        datetime = dateparse.parse_datetime(f'{date} {time}')

        Tag.objects.create_tag(initiating_player, receiving_player, datetime, location, description)
        messages.add_message(request, messages.INFO, f'Reported a tag on {receiving_player.user.get_full_name()}')

    return redirect('dashboard')
