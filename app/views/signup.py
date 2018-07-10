from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from app.models import SignupInvite, User, Player, PlayerRole
from app.util import require_post_parameters, most_recent_game, game_required


def signup(request, signup_invite):
    invite = get_object_or_404(SignupInvite, pk=signup_invite)
    if User.objects.filter(email=invite.email).exists():
        return redirect('game_signup')
    else:
        return redirect('user_signup', signup_invite=signup_invite)


class UserSignupView(View):
    def get(self, request, **kwargs):
        signup_invite = kwargs['signup_invite']
        invite = get_object_or_404(SignupInvite, pk=signup_invite)
        if invite.used_at:
            messages.info(request, f'You\'ve already created an account using {invite.email}.')
            return redirect('dashboard')

        return render(request, 'registration/user_signup.html', {'signup_invite': signup_invite})

    def post(self, request, signup_invite):
        invite = get_object_or_404(SignupInvite, pk=signup_invite)
        if invite.used_at:
            messages.info(request, f'You\'ve already created an account using {invite.email}.')
            return redirect('dashboard')

        first_name, last_name, password1, password2 = \
            require_post_parameters(request, 'first_name', 'last_name', 'password1', 'password2')

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
@method_decorator(game_required, name='dispatch')
class GameSignupView(View):
    def get(self, request):
        game = most_recent_game()
        forced_role = SignupInvite.objects.filter(used_at__isnull=False, email=request.user.email).get().player_role

        if not game.is_finished and not request.user.player_set.filter(game=game, active=True).exists():
            return render(request, 'registration/game_signup.html', {'game': game, 'player_role': forced_role})
        else:
            messages.warning(request, "You're already signed up for the game.")
            return redirect('dashboard')

    def post(self, request):
        game = most_recent_game()
        forced_role = SignupInvite.objects.filter(used_at__isnull=False, email=request.user.email).get().player_role
        in_oz_pool = request.POST.get('is_oz', 'off') == 'on'
        has_signed_waiver = request.POST.get('accept_waiver', 'off') == 'on'

        if not has_signed_waiver:
            messages.warning(request, 'Please sign the waiver.')
            return self.get(request)

        if request.user.player_set.filter(game=game, active=True).exists():
            messages.warning(request, "You're already signed up for the game.")
            return redirect('dashboard')

        if forced_role:
            Player.objects.create_player(request.user, game, forced_role)
        else:
            Player.objects.create_player(request.user, game, PlayerRole.HUMAN, in_oz_pool=in_oz_pool)

        messages.success(request, f'You\'ve successfully signed up for the {game} game.')
        return redirect('dashboard')
