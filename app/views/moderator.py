from django.contrib import messages
from django.utils.decorators import method_decorator

from app.mail import send_signup_email
from app.models import Player, SignupLocation, User
from app.util import moderator_required, require_post_parameters, MobileSupportedView, active_game


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
        game = active_game()
        return self.mobile_or_desktop(request, {'signup_locations': locations, 'game': game})

    def post(self, request):
        location_id, email = require_post_parameters(request, 'signup_location', 'email')
        if User.objects.filter(email=email).exists():
            messages.add_message(request, messages.WARNING, f'There is already an account associated with: {email}.')
            return self.get(request)

        location = SignupLocation.objects.get(pk=location_id)
        game = active_game()
        send_signup_email(request, game, location, email)
        messages.success(request, f'Sent an email to: {email}.')
        return self.get(request)


@method_decorator(moderator_required, name='dispatch')
class SignupLocationsView(MobileSupportedView):
    desktop_template = 'dashboard/signup_locations.html'
    mobile_template = 'dashboard/signup_locations.html'

    def get(self, request):
        locations = SignupLocation.objects.all()
        return self.mobile_or_desktop(request, {'signup_locations': locations})
