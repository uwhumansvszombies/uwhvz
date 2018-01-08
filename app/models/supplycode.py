import uuid

from django.db import models

from .player import Player


class SupplyCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=6, unique=True)
    claimed_by = models.ForeignKey(Player, on_delete=models.CASCADE)
    claimed_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
