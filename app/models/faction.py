import uuid
from datetime import datetime

from django.db import models

from .game import Game

class FactionManager(models.Manager):
    def create_faction(self, game: Game, name: str, description: str) -> 'Faction':
        if Faction.objects.filter(game=game, name=name):
            raise ValueError(f"The faction {faction} already exists in the game {game}.")

        faction = self.model(name=name, game=game, description=description)
        faction.save()
        return faction

class Faction(models.Model):
    id: uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    game: Game = models.ForeignKey(Game, on_delete=models.PROTECT, null=True)
    name: str = models.CharField(max_length=100)
    description: str = models.TextField(blank=True)

    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    objects = FactionManager()

    def __str__(self):
        return self.name
