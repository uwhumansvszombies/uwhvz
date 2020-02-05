from rest_framework import serializers
from app.models import Modifier


class ModifierSerializer(serializers.ModelSerializer):

    type = serializers.SerializerMethodField("getTypeString")

    def getTypeString(self, modifier):
        return modifier.modifier_type.value

    class Meta:
        model = Modifier
        fields = ['modifier_amount', 'type']
