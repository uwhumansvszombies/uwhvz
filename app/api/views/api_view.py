from app.serializers.player_serializer import PlayerSerializer
from app.models import Player, Spectator, Moderator
from app.api.util import *

from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt

import json

def account_info(request):
    if not request.user.is_authenticated:
        return unauthorized([])

    if request.method == "GET":
        playerSet = Player.objects.all().filter(user=request.user)
        if playerSet:
            player = playerSet[0]
            serializer = PlayerSerializer(player)
            return success(serializer.data)
        else:
            return unauthorized([])

@csrf_exempt
def view_login(request):
    if request.method == "GET":
        return notFound([])
    
    elif request.method == "POST":
        user = authenticate(email = request.POST.get('username'), password = request.POST.get('password'))

        if user is None:
            return unauthorized([])
        else:
            login(request, user)
            return success("success")

def view_logout(request):
    if request.method == "GET": 
        if request.user.is_authenticated:
            logout(request)
            return success("Success")
        else:
            return unauthorized("Logout Failed")
    
    elif request.method == "POST":
        return notFound([])