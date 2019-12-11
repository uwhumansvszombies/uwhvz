import uuid
from datetime import datetime

from django.db import models

from .game import Game
from .player import Player


class PurchaseManager(models.Manager):
    def create_purchase(self, buyer: Player, cost: int, game: Game, details: str) -> 'Purchase':
        purchase = self.model(buyer=buyer, cost=cost, game=game, details=details)
        purchase.save()
        return purchase


class Purchase(models.Model):
    id: uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game: Game = models.ForeignKey(Game, on_delete=models.CASCADE)
    cost: int = models.IntegerField()
    details: str = models.CharField(blank=True,max_length=50)
    
    buyer: Player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True, related_name='buyer_name')
    
    active: bool = models.BooleanField(default=True)

    time: datetime = models.DateTimeField(auto_now_add=True)
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    objects = PurchaseManager()

    def __int__(self):
        return self.cost