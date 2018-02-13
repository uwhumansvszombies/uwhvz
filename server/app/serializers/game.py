from rest_framework import serializers
from app.models import Game


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'game_name', 'created_at', 'modified_at')
        lookup_field = 'game_name'
