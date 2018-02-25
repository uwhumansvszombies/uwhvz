from rest_framework import generics
from app.serializers import PlayerSerializer
from app.models import Player


class PlayerCreateView(generics.ListCreateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    def perform_create(self, serializer):
        serializer.save()


class PlayerDetailsView(generics.RetrieveUpdateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
