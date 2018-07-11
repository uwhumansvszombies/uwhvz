from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from app.models import SignupInvite, User, Player, PlayerRole
from app.util import most_recent_game, game_required
from .forms import UserSignupForm


def signup(request, signup_invite):
    invite = get_object_or_404(SignupInvite, pk=signup_invite)
    if User.objects.filter(email=invite.email).exists():
        return redirect('game_signup')
    else:
        return redirect('user_signup', signup_invite=signup_invite)


class UserSignupView(View):
    template_name = "registration/user_signup.html"

    def dispatch(self, request, *args, **kwargs):
        signup_invite = get_object_or_404(SignupInvite, pk=kwargs.get('signup_invite'))
        if signup_invite.used_at:
            messages.info(request, f"You've already created an account using {signup_invite.email}.")
            return redirect('dashboard')
        kwargs.update({'signup_invite': signup_invite})
        return super().dispatch(request, *args, **kwargs)

    def render_user_signup(self, request, signup_invite: SignupInvite, user_signup_form=UserSignupForm()):
        return render(request, self.template_name, {
            'signup_invite': signup_invite,
            'user_signup_form': user_signup_form
        })

    def get(self, request, signup_invite: SignupInvite):
        return self.render_user_signup(request, signup_invite)

    def post(self, request, signup_invite: SignupInvite):
        user_signup_form = UserSignupForm(request.POST)
        if not user_signup_form.is_valid():
            return self.render_user_signup(request, signup_invite, user_signup_form=user_signup_form)

        cleaned_data = user_signup_form.cleaned_data
        first_name, last_name, password = cleaned_data['first_name'], cleaned_data['last_name'], cleaned_data[
            'password1']

        with transaction.atomic():
            User.objects.create_user(signup_invite.email, password, first_name=first_name, last_name=last_name)
            signup_invite.used_at = timezone.now()
            signup_invite.save()

        user = authenticate(username=signup_invite.email, password=password)
        login(request, user)
        return redirect('game_signup')


@method_decorator(login_required, name='dispatch')
@method_decorator(game_required, name='dispatch')
class GameSignupView(View):
    def get(self, request):
        game = most_recent_game()
        forced_role = SignupInvite.objects.filter(used_at__isnull=False, email=request.user.email).get().player_role

        if not game.is_finished and not request.user.player_set.filter(game=game, active=True).exists():
            return render(request, "registration/game_signup.html", {'game': game, 'player_role': forced_role})
        else:
            messages.warning(request, "You're already signed up for the game.")
            return redirect('dashboard')

    def post(self, request):
        game = most_recent_game()
        forced_role = SignupInvite.objects.filter(used_at__isnull=False, email=request.user.email).get().player_role
        in_oz_pool = request.POST.get('is_oz', 'off') == 'on'
        has_signed_waiver = request.POST.get('accept_waiver', 'off') == 'on'

        if not has_signed_waiver:
            messages.warning(request, "Please sign the waiver.")
            return self.get(request)

        if request.user.player_set.filter(game=game, active=True).exists():
            messages.warning(request, "You're already signed up for the game.")
            return redirect('dashboard')

        if forced_role:
            Player.objects.create_player(request.user, game, forced_role)
        else:
            Player.objects.create_player(request.user, game, PlayerRole.HUMAN, in_oz_pool=in_oz_pool)

        messages.success(request, f"You've successfully signed up for the {game} game.")
        return redirect('dashboard')
