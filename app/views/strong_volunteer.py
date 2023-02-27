from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from random import choices
from string import ascii_letters, digits, punctuation

from app.mail import send_signup_email
from app.models import SignupInvite, SignupLocation, User, Player, PlayerRole
from app.util import volunteer_required, most_recent_game, signups_game_required, running_game_required
from .forms import StrongVolunteerSignupPlayerForm

@method_decorator(running_game_required, name='dispatch')
class BetterSignupPlayersView(View):
    template_name = "dashboard/strong_volunteer/signup_players.html"

    def render_signup_players(self, request, volunteer_signup_player_form=StrongVolunteerSignupPlayerForm()):
        game = most_recent_game()
        locations = SignupLocation.objects.filter(game=game)

        return render(request, self.template_name, {
            'game': game,
            'participant': request.user.participant(game),
            'volunteer_signup_player_form': volunteer_signup_player_form,
        })

    def get(self, request):
        return self.render_signup_players(request)

    def post(self, request):
        volunteer_signup_player_form = StrongVolunteerSignupPlayerForm(request.POST)
        if not volunteer_signup_player_form.is_valid():
            return self.render_signup_players(request, volunteer_signup_player_form=volunteer_signup_player_form)

        has_signed_waiver = request.POST.get('accept_waiver', 'off') == 'on'

        if not has_signed_waiver:
            messages.warning(request, "Please sign the waiver.")
            return self.render_signup_players(request, volunteer_signup_player_form=volunteer_signup_player_form)

        game = most_recent_game()
        cleaned_data = volunteer_signup_player_form.cleaned_data
        first_name = cleaned_data['first_name']
        last_name = cleaned_data['last_name']
        email = cleaned_data['email']

        # Create user object if no account exists
        
        if not User.objects.filter(email=email).exists():
            tmp_password = ''.join(choices(ascii_letters + digits + punctuation, k=10))
            User.objects.create_user(email, tmp_password, first_name=first_name, last_name=last_name)

            # Send reset password email
            fake_form = PasswordResetForm({'email': email})

            if not fake_form.is_valid():
                messages.warning(request, "Password reset form failure")
                return self.render_signup_players(request, volunteer_signup_player_form=volunteer_signup_player_form)

            fake_form.save(request=request, use_https=True, from_email=settings.DEFAULT_FROM_EMAIL, email_template_name='registration/password_reset_email.html')

        # Create player object as human

        user = User.objects.get(email=email)
        player = ''
        start_msg = ''

        if user.participant(game):
            player = user.participant(game)

            start_msg = f"{email} is already signed up for {game}!"
        else:
            Player.objects.create_player(user, game, PlayerRole.HUMAN, in_oz_pool=True)
            player = user.participant(game)

            start_msg = f"{email} is now signed up for {game}."


        # Add player code to message
        player = user.participant(game)
        code = player.code

        messages.success(request, f"{start_msg} Your player code is {code}.")
        return redirect('better_signup_players')
