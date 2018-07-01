from django.contrib import messages
from django.utils.decorators import method_decorator

from app.mail import send_signup_email
from app.models import Player, SignupLocation, User, SupplyCode
from app.util import moderator_required, require_post_parameters, MobileSupportedView, active_game


@method_decorator(moderator_required, name='dispatch')
class PlayerListView(MobileSupportedView):
    desktop_template = 'dashboard/moderator/player_list.html'
    mobile_template = 'dashboard/moderator/player_list.html'

    def get(self, request):
        players = Player.objects.all()
        game = active_game()
        return self.mobile_or_desktop(request, {
            'player': request.user.player(game),
            'players': players
        })


@method_decorator(moderator_required, name='dispatch')
class AddPlayerView(MobileSupportedView):
    desktop_template = 'dashboard/moderator/add_player.html'
    mobile_template = 'dashboard/moderator/add_player.html'

    def get(self, request):
        locations = SignupLocation.objects.all()
        game = active_game()
        return self.mobile_or_desktop(request, {
            'player': request.user.player(game),
            'signup_locations': locations,
            'game': game
        })

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
    desktop_template = 'dashboard/moderator/signup_locations.html'
    mobile_template = 'dashboard/moderator/signup_locations.html'

    def get(self, request):
        locations = SignupLocation.objects.all()
        game = active_game()
        return self.mobile_or_desktop(request, {
            'player': request.user.player(game),
            'signup_locations': locations
        })


@method_decorator(moderator_required, name='dispatch')
class GenerateSupplyCodeView(MobileSupportedView):
    desktop_template = 'dashboard/moderator/generate_supply_codes.html'
    mobile_template = 'dashboard/moderator/generate_supply_codes.html'

    def get(self, request):
        supply_codes = SupplyCode.objects.all()
        game = active_game()
        return self.mobile_or_desktop(request, {
            'player': request.user.player(game),
            'supply_codes': supply_codes
        })

    def post(self, request):
        game = active_game()
        supply_code = SupplyCode.objects.create_supply_code(game)
        messages.success(request, f'Generated new code: {supply_code}.')
        return self.get(request)
