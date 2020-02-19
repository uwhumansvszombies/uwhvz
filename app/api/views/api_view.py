from app.serializers.player_serializer import PlayerSerializer
from app.models import Player, Spectator, Moderator, Modifier, Tag
from app.models.modifier import ModifierType
from app.api.util import *
from app.mail import send_tag_email, send_stun_email
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

import json

def account_info(request):
    if not request.user.is_authenticated:
        return unauthorized()

    if request.method == "GET":
        playerSet = Player.objects.all().filter(user=request.user)
        if playerSet:
            player = playerSet[0]
            serializer = PlayerSerializer(player)
            return success(serializer.data)
        else:
            return forbidden()

def stun_tag(request):
    if not request.user.is_authenticated:
        return unauthorized()
    
    if request.method == "GET":
        return notFound()
    
    elif request.method == "POST":
        player = Player.objects.get(user=request.user)
        if not Player:
            return forbidden()

        code = request.POST.get('code') or ""
        code = code.upper()
        try:
            target = Player.objects.get(code=code, active=True)
        except ObjectDoesNotExist:
            return notFound("Player not found") 

        time = int(request.POST.get('time'))
        if type(time) != int:
            return badRequest()

        date = datetime.fromtimestamp(time)
        location = request.POST.get('location') or ""
        description = request.POST.get('description') or ""

        tag_modifier_amount = 0
        try:
            tag_modifier = Modifier.objects.get(faction=player.faction, modifier_type=ModifierType.TAG)
            tag_modifier_amount = tag_modifier.modifier_amount
        except ObjectDoesNotExist:
            pass

        if Tag.objects.filter(initiator=player, receiver=target,
                              tagged_at=date, location=location,
                              description=description):
            return conflictOrDuplicate()

        try:
            tag = Tag.objects.create_tag(player, target, date,
                                         location, description, tag_modifier_amount)
            tag.active = False
            tag.save()
        except ValueError as err:
            return badRequest("Error creating tag")

        if player.is_human:
            send_stun_email(request, tag)
        else:
            send_tag_email(request, tag)
        return success(target.user.get_full_name())

@csrf_exempt
def view_login(request):
    if request.method == "GET":
        return notFound()
    
    elif request.method == "POST":
        user = authenticate(email = request.POST.get('username'), password = request.POST.get('password'))

        if user is None:
            return unauthorized()
        else:
            login(request, user)
            return success("success")

def view_logout(request):
    if request.method == "GET": 
        if request.user.is_authenticated:
            logout(request)
            return success("Success")
        else:
            return forbidden("Logout Failed")
    
    elif request.method == "POST":
        return notFound()
