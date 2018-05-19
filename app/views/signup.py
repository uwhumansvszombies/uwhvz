from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import SignupToken, User, Game, Player, PlayerRole
from app.util import require_post_parameters


def signup(request, signup_token):
    token = SignupToken.objects.get(pk=signup_token)
    if User.objects.filter(email=token.email).exists():
        return redirect('game_signup')
    else:
        return redirect('user_signup', signup_token=signup_token)


def user_signup(request, signup_token):
    token = SignupToken.objects.get(pk=signup_token)
    if token.used_at:
        messages.add_message(request, messages.INFO, f'You\'ve already created an account using {token.email}.')
        return redirect('dashboard')

    if request.method == 'POST':
        first_name, last_name, password = require_post_parameters(request, 'first_name', 'last_name', 'password')
        with transaction.atomic():
            User.objects.create_user(token.email, password, first_name=first_name, last_name=last_name)
            token.used_at = timezone.now()
            token.save()

        user = authenticate(username=token.email, password=password)
        login(request, user)
        return redirect('game_signup')

    return render(request, 'dashboard/user_signup.html', {'signup_token': signup_token})


@login_required
def game_signup(request):
    if request.method == 'POST':
        game_id, = require_post_parameters(request, 'game')
        in_oz_pool = request.POST.get('is_oz', 'off') == 'on'
        game = Game.objects.get(pk=game_id)
        Player.objects.create_player(request.user, game, PlayerRole.HUMAN, in_oz_pool=in_oz_pool)
        return redirect('dashboard')

    games = Game.objects.all()
    return render(request, 'dashboard/game_signup.html', {'games': games})
