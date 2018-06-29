from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.utils import dateparse
from django.utils.decorators import method_decorator

from app.models import Player, Tag
from app.util import require_post_parameters, MobileSupportedView, active_game


class IndexView(MobileSupportedView):
    desktop_template = 'index.html'
    mobile_template = 'index.html'


@method_decorator(login_required, name='dispatch')
class DashboardView(MobileSupportedView):
    desktop_template = 'dashboard/index.html'
    mobile_template = 'dashboard/index.html'

    def get(self, request):
        game = active_game()
        if not game.started_on:
            return render(request, 'dashboard/game_not_started.html')

        try:
            player = request.user.player_set.get()
        except ObjectDoesNotExist:
            messages.info(request, "You haven't signed up for any games yet.")
            return redirect('game_signup')
        team_score = sum([p.score() for p in Player.objects.all()])
        return self.mobile_or_desktop(request, {'player': player, 'team_score': team_score})


@method_decorator(login_required, name='dispatch')
class ReportTagView(MobileSupportedView):
    def post(self, request):
        player_code, date, time, location, description = \
            require_post_parameters(request, 'player_code', 'date', 'time', 'location', 'description')
        game = active_game()
        initiating_player = request.user.player(game)
        receiving_player = Player.objects.get(code=player_code)
        # TODO: Time zone?
        datetime = dateparse.parse_datetime(f'{date} {time}')

        Tag.objects.create_tag(initiating_player, receiving_player, datetime, location, description)
        messages.info(request, f'Reported a tag on {receiving_player.user.get_full_name()}')
        return redirect('dashboard')

    def get(self, request):
        return redirect('dashboard')
