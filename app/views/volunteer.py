from django.contrib import messages
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from app.mail import send_signup_email
from app.models import SignupLocation, User
from app.util import volunteer_required, most_recent_game, require_post_parameters


@method_decorator(volunteer_required, name='dispatch')
class SignUpPlayersView(View):
    template_name = 'dashboard/volunteer/signup_players.html'

    def get(self, request):
        locations = SignupLocation.objects.all()
        game = most_recent_game()
        return render(request, self.template_name, {
            'game': game,
            'player': request.user.player(game),
            'signup_locations': locations,
        })

    def post(self, request):
        location_id, email = require_post_parameters(request, 'signup_location', 'email')
        if User.objects.filter(email=email).exists():
            messages.warning(request, f'There is already an account associated with: {email}.')
            return self.get(request)

        location = SignupLocation.objects.get(pk=location_id)
        game = most_recent_game()
        send_signup_email(request, game, location, email)
        messages.success(request, f'Sent an email to: {email}.')
        return self.get(request)
