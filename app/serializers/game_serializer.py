from rest_framework import serializers
from app.models import Game, GameState

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['name',
            'status',
            'started_on',
            'ended_on']
    
    status = serializers.SerializerMethodField('getStatus')

    def getStatus(self, game):
        state = game.state()
        if state == GameState.FINISHED:
            return "finished"
        elif state == GameState.RUNNING:
            return "running"
        elif state == GameState.SIGNUPS:
            return "signups"
