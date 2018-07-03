from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from app.models import SignupInvite, User, Player, PlayerRole
from app.util import require_post_parameters, most_recent_game, active_game_required


def signup(request, signup_invite):
    invite = SignupInvite.objects.get(pk=signup_invite)
    if User.objects.filter(email=invite.email).exists():
        return redirect('game_signup')
    else:
        return redirect('user_signup', signup_invite=signup_invite)


class UserSignupView(View):
    def get(self, request, **kwargs):
        signup_invite = kwargs['signup_invite']
        invite = SignupInvite.objects.get(pk=signup_invite)
        if invite.used_at:
            messages.info(request, f'You\'ve already created an account using {invite.email}.')
            return redirect('dashboard')

        return render(request, 'registration/user_signup.html', {'signup_invite': signup_invite})

    def post(self, request, signup_invite):
        invite = SignupInvite.objects.get(pk=signup_invite)
        if invite.used_at:
            messages.info(request, f'You\'ve already created an account using {invite.email}.')
            return redirect('dashboard')

        first_name, last_name, password1, password2 = require_post_parameters(request, 'first_name', 'last_name', 'password1', 'password2')

        if password1 != password2:
            messages.error(request, "The passwords do not match.")
            return self.get(request, signup_invite=signup_invite)

        with transaction.atomic():
            User.objects.create_user(invite.email, password1, first_name=first_name, last_name=last_name)
            invite.used_at = timezone.now()
            invite.save()

        user = authenticate(username=invite.email, password=password1)
        login(request, user)
        return redirect('game_signup')


@method_decorator(login_required, name='dispatch')
@method_decorator(active_game_required, name='dispatch')
class GameSignupView(View):
    def get(self, request):
        game = most_recent_game()
        if request.user.player(game).exists():
            return redirect('dashboard')
        return render(request, 'registration/game_signup.html', {'game': game})

    def post(self, request):
        in_oz_pool = request.POST.get('is_oz', 'off') == 'on'
        game = most_recent_game()
        if request.user.player(game).exists():
            return redirect('dashboard')
        Player.objects.create_player(request.useir, game, PlayerRole.HUMAN, in_oz_pool=in_oz_pool)
        return redirect('dashboard')
