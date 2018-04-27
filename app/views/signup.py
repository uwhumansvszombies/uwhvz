from django.shortcuts import render, redirect

from app.models import SignupToken, User
from app.util import check_argument


def signup(request, signup_token):
    token = SignupToken.objects.get(pk=signup_token)
    if token.used_at:
        return "You're already signed up!"
    if User.objects.filter(email=token.email).exists():
        redirect('game_signup')
    else:
        redirect('user_signup')


def signup_user(request, signup_token):
    if request.method == 'POST':
        _game = request.POST.get('game')
        _location = request.POST.get('signup_location')
        email = request.POST.get('email')
        check_argument(request, _game, 'Game cannot be blank.')
        check_argument(request, _location, 'Signup location cannot be blank.')
        check_argument(request, email, 'Email cannot be blank.')
        # Handle user creation and stuff
        redirect('game_signup')

    return render(request, '???/signup_user.html')


def signup_for_game(request):
    pass
