from rest_framework import serializers
from app.models import Faction, Modifier
from app.serializers.modifier_serializer import ModifierSerializer

class FactionSerializer(serializers.ModelSerializer):
    modifiers = serializers.SerializerMethodField("getModifiers")

    def getModifiers(self, faction): 
        return list(map(self.serializeModifiers, Modifier.objects.filter(faction = faction)))
        
    def serializeModifiers(self, modifier):
        return ModifierSerializer(modifier).data

    class Meta:
        model = Faction
        fields = ['name', 'description', 'modifiers']
