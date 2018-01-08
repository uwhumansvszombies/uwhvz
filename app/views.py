from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from app.models import Game, Player


def index(request):
    return render(request, 'index.html')


@login_required
def dashboard(request):
    # TODO: find the active game, not just the first game you can!
    game = Game.objects.all()[0]
    player = Player.objects.get(game=game, user=request.user)

    return render(request, 'dashboard/dashboard.html', {
        'game': game,
        'player': player,
    })
