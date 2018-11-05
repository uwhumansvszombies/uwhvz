import uuid
from datetime import datetime

from django.db import models, transaction, DatabaseError
from django.utils import timezone

from .game import Game
from .player import Player
from .util import generate_code


class SupplyCodeManager(models.Manager):
    def create_supply_code(self, game: Game, value: int = 5) -> 'SupplyCode':
        code = generate_code(6)
        # For set of all supply codes, each code must be unique
        while self.filter(code=code):
            code = generate_code(6)

        supply_code = self.model(code=code, game=game, value=value)
        supply_code.save()
        return supply_code


class SupplyCode(models.Model):
    id: uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    game: Game = models.ForeignKey(Game, on_delete=models.CASCADE)
    code: str = models.CharField(max_length=6, unique=True)
    value: int = models.IntegerField()
    point_modifier: int = models.IntegerField(default=0)
    active: bool = models.BooleanField(default=True)

    claimed_by: Player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True)
    claimed_at: datetime = models.DateTimeField(null=True, blank=True)

    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    objects = SupplyCodeManager()

    def claim(self, player: Player, point_modifier: int) -> 'SupplyCode':
        self.claimed_by = player
        self.claimed_at = timezone.now()
        self.point_modifier = point_modifier
        try:
            with transaction.atomic():
                self.save()
        except DatabaseError:
            self.claimed_by = None
            self.claimed_at = None
            self.point_modifier = 0
        return self

    def __str__(self):
        return self.code
