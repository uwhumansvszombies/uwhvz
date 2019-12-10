import uuid
from datetime import datetime

from django.db import models

from .game import Game
from .player import Player


class PurchaseManager(models.Manager):
    def create_purchase(self, cost: int, game: Game) -> 'Purchase':
        purchase = self.model(cost=cost, game=game)
        purchase.save()
        return signup_location


class Purchase(models.Model):
    id: uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game: Game = models.ForeignKey(Game, on_delete=models.CASCADE)
    cost: int = models.IntegerField()
    
    buyer: Player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True, related_name='buyer_name')
    
    active: bool = models.BooleanField(default=True)

    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    objects = PurchaseManager()

    def __int__(self):
        return self.cost