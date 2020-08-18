from rest_framework import serializers
from app.models import Tag
from django.db import models
from enumfields import EnumField, Enum

class TagSerializer(serializers.ModelSerializer):

    initiator_name = serializers.SerializerMethodField('getInitiatorName')
    
    def getInitiatorName(self, tag):
        return tag.initiator.user.get_full_name()
    
    initiator_role = serializers.SerializerMethodField('getInitiatorRole')

    def getInitiatorRole(self, tag):
        return tag.initiator.role.value
    
    receiver_name = serializers.SerializerMethodField('getReceiverName')
    
    def getReceiverName(self, tag):
        return tag.receiver.user.get_full_name()

    receiver_role = serializers.SerializerMethodField('getReceiverRole')

    def getReceiverRole(self, tag):
        return tag.receiver.role.value

    points = serializers.SerializerMethodField('getPoints')

    def getPoints(self, tag):
        return tag.receiver.value(tag.tagged_at) + tag.point_modifier

    time = serializers.SerializerMethodField('getTimeCreated')
        
    def getTimeCreated(self, tag): 
        return tag.created_at

    tag_type = serializers.SerializerMethodField('getTagType')

    def getTagType(self, tag):
        return tag.type.value

    class Meta:
        model = Tag
        fields = [
            'initiator_name',
            'initiator_role',
            'receiver_name',
            'receiver_role',
            'points',
            'location',
            'time',
            'tag_type']

