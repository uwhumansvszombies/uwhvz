from rest_framework import serializers
from app.models import Moderator, Spectator
from django.db import models

class SimpleModeratorSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('getName')

    def getName(self, mod):
        return mod.user.get_full_name()

    score = serializers.SerializerMethodField('getProcessedScore')

    def getProcessedScore(self, mod):
        if mod.score is None:
            return "N/A"
        else:
            return mod.score
    
    class Meta:
        model = Moderator
        fields = ['name', 'score']

class SpectatorSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('getName')

    def getName(self, spectator):
        return spectator.user.get_full_name()

    class Meta:
        model = Spectator
        fields = ['name']
