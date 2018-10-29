from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from app.mail import send_signup_email
from app.models import SignupInvite, SignupLocation, User
from app.util import volunteer_required, most_recent_game, active_game_required
from .forms import VolunteerSignupPlayerForm


@method_decorator(volunteer_required, name='dispatch')
@method_decorator(active_game_required, name='dispatch')
class SignupPlayersView(View):
    template_name = "dashboard/volunteer/signup_players.html"

    def render_signup_players(self, request, volunteer_signup_player_form=VolunteerSignupPlayerForm()):
        game = most_recent_game()
        locations = SignupLocation.objects.all()

        return render(request, self.template_name, {
            'game': game,
            'signup_locations': locations,
            'volunteer_signup_player_form': volunteer_signup_player_form
        })

    def get(self, request):
        return self.render_signup_players(request)

    def post(self, request):
        volunteer_signup_player_form = VolunteerSignupPlayerForm(request.POST)
        if not volunteer_signup_player_form.is_valid():
            return self.render_signup_players(request, volunteer_signup_player_form=volunteer_signup_player_form)

        game = most_recent_game()
        cleaned_data = volunteer_signup_player_form.cleaned_data
        location, email = cleaned_data['location'], cleaned_data['email']

        if User.objects.filter(email=email).exists():
            messages.warning(request, f"There is already an account associated with: {email}.")
            return redirect('signup_players')

        signup_invite = SignupInvite.objects.create_signup_invite(game, location, email)
        send_signup_email(request, signup_invite)
        messages.success(request, f"Sent a signup email to {email}.")
        return redirect('signup_players')
