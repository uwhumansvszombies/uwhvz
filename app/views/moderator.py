from django.contrib import messages
from django.utils.decorators import method_decorator

from app.mail import send_signup_email
from app.models import Player, SignupLocation, Game
from app.util import moderator_required, require_post_parameters, MobileSupportedView


@method_decorator(moderator_required, name='dispatch')
class PlayerListView(MobileSupportedView):
    desktop_template = 'dashboard/player_list.html'
    mobile_template = 'dashboard/player_list.html'

    def get(self, request):
        players = Player.objects.all()
        return self.mobile_or_desktop(request, {'players': players})


@method_decorator(moderator_required, name='dispatch')
class AddPlayerView(MobileSupportedView):
    desktop_template = 'dashboard/add_player.html'
    mobile_template = 'dashboard/add_player.html'

    def get(self, request):
        locations = SignupLocation.objects.all()
        games = Game.objects.all()
        return self.mobile_or_desktop(request, {'signup_locations': locations, 'games': games})

    def post(self, request):
        game_id, location_id, email = require_post_parameters(request, 'game', 'signup_location', 'email')
        location = SignupLocation.objects.get(pk=location_id)
        game = Game.objects.get(pk=game_id)
        send_signup_email(request, game, location, email)
        messages.add_message(request, messages.SUCCESS, f'Sent an email to: {email}')
        return self.get(request)


@method_decorator(moderator_required, name='dispatch')
class SignupLocationsView(MobileSupportedView):
    desktop_template = 'dashboard/add_player.html'
    mobile_template = 'dashboard/add_player.html'

    def get(self, request):
        locations = SignupLocation.objects.all()
        return self.mobile_or_desktop(request, {'signup_locations': locations})
