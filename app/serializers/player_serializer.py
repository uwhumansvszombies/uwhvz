from rest_framework import serializers
from app.models import Player
from django.db import models
from enumfields import EnumField, Enum
from app.models.player import PlayerRole
from app.serializers import FactionSerializer, GameSerializer

class PlayerSerializer(serializers.ModelSerializer):
    roleChar = serializers.SerializerMethodField('getRole')

    def getRole(self, player):
        return player.role.value

    name = serializers.SerializerMethodField('getName')

    def getName(self, player):
        return player.user.get_full_name()

    email = serializers.SerializerMethodField('getEmail')

    def getEmail(self, player):
        return player.user.email

    faction = FactionSerializer()
    game = GameSerializer()
    
    class Meta:
        model = Player
        fields = ['code', 
            'roleChar', 
            'is_oz',
            'name',
            'email',
            'score',
            'shop_score',
            'game',
            'faction']

    point_modifier: int = models.IntegerField(default=0)
    