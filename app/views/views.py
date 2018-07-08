from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import dateparse
from django.utils.decorators import method_decorator
from django.views import View

from app.models import Player, Tag, SupplyCode
from app.util import require_post_parameters, MobileSupportedView, game_exists, most_recent_game, running_game_required


class IndexView(MobileSupportedView):
    desktop_template = 'index.html'
    mobile_template = 'index.html'


@method_decorator(login_required, name='dispatch')
class DashboardView(MobileSupportedView):
    desktop_template = 'dashboard/index.html'
    mobile_template = 'dashboard/index.html'

    def get(self, request):
        if game_exists():
            game = most_recent_game()            
            if game.is_active:
                if not Player.objects.filter(game=game, user=request.user).exists():
                    game_signup_url = reverse('game_signup')
                    messages.warning(request, f'You haven\'t finished signing up for the {game} game. '
                                              f'If you still wish to join, '
                                              f'<a href="{game_signup_url}">you can finish signing up here</a>.')

            return self.mobile_or_desktop(request, {'game': game})
        return self.mobile_or_desktop(request)


@method_decorator(login_required, name='dispatch')
@method_decorator(running_game_required, name='dispatch')
class PlayerInfoView(MobileSupportedView):
    desktop_template = 'dashboard/player.html'
    mobile_template = 'dashboard/player.html'

    def get(self, request):
        game = most_recent_game()
        try:
            player = request.user.player_set.get(game=game, active=True)
        except ObjectDoesNotExist:
            return redirect('dashboard')
        team_score = sum([p.score() for p in Player.objects.filter(role=player.role).all()])
        return self.mobile_or_desktop(request, {'game': game, 'player': player, 'team_score': team_score})


@method_decorator(login_required, name='dispatch')
@method_decorator(running_game_required, name='dispatch')
class ReportTagView(View):
    def get(self):
        return redirect('player_info')

    def post(self, request):
        player_code, date, time, location, description = \
            require_post_parameters(request, 'player_code', 'date', 'time', 'location', 'description')
        game = most_recent_game()
        initiating_player = request.user.player(game)
        try:
            receiving_player = Player.objects.get(code=player_code, active=True)
        except ObjectDoesNotExist:
            messages.error(request, 'We can\'t find a player associated with that code.')
            return redirect('player_info')
        # TODO: Time zone?
        datetime = dateparse.parse_datetime(f'{date} {time}')

        Tag.objects.create_tag(initiating_player, receiving_player, datetime, location, description)
        messages.info(request, f'You\'ve reported a tag on {receiving_player.user.get_full_name()}.')
        return redirect('player_info')


@method_decorator(login_required, name='dispatch')
@method_decorator(running_game_required, name='dispatch')
class ClaimSupplyCodeView(View):
    def get(self):
        return redirect('player_info')

    def post(self, request):
        # since what's returned is a list, we need to keep the comma there 
        # so it "dereferences" the list and returns just the string/code value itself
        code, = require_post_parameters(request, 'supply_code')
        try:
            supply_code = SupplyCode.objects.get(code=code, claimed_by__isnull=True)
            print(supply_code)
        except ObjectDoesNotExist:
            messages.error(request, "That supply code does not exist or has already been redeemed.")
            return redirect('player_info')

        game = most_recent_game()
        player = request.user.player(game)
        if not player.is_human:
            messages.error(request, "Only humans can claim supply codes.")
            return redirect('player_info')

        supply_code.claim(player)
        messages.success(request, 'The code has been redeemed successfully.')
        return redirect('player_info')


@method_decorator(login_required, name='dispatch')
@method_decorator(running_game_required, name='dispatch')
class PlayerListView(View):
    template_name = 'dashboard/player_list.html'

    def get(self, request):
        players = Player.objects.all()
        game = most_recent_game()
        return render(request, self.template_name, {
            'game': game,
            'player': request.user.player(game),
            'players': players
        })
