from rest_framework import serializers
from app.models import Player
from drf_enum_field.serializers import EnumFieldSerializerMixin


class PlayerSerializer(EnumFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'user', 'game', 'code', 'role')
