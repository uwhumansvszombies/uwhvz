from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from app.models import Game, Player


def index(request):
    return render(request, 'index.html')


@login_required
def dashboard(request):
    game = Game.objects.all().filter(is_active)
    player = Player.objects.all(game=game, user=request.user)
    return render(request, 'dashboard/dashboard.html', {
        'game': game,
        'player': player
    })
