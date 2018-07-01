import uuid

from django.db import models, transaction, DatabaseError
from django.utils import timezone

from app.models.util import generate_code
from .game import Game
from .player import Player


class SupplyCodeManager(models.Manager):
    def create_supply_code(self, game, value=5):
        code = generate_code(6)
        # For set of all supply codes, each code must be unique
        while self.filter(code=code):
            code = generate_code(6)

        supply_code = self.model(code=code, game=game, value=value)
        supply_code.save()
        return supply_code


class SupplyCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)
    value = models.IntegerField()
    claimed_by = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True)
    claimed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = SupplyCodeManager()

    def claim(self, player):
        self.claimed_by = player
        self.claimed_at = timezone.now()
        try:
            with transaction.atomic():
                self.save()
        except DatabaseError:
            self.claimed_by = None
            self.claimed_at = None
        return self

    def __str__(self):
        return self.code
