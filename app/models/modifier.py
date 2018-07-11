import uuid
from datetime import datetime

from django.db import models
from enumfields import Enum, EnumField

from .faction import Faction


class ModifierType(Enum):
    ONE_TIME_USE: Enum = 'O'
    SUPPLY_CODE: Enum = 'S'
    TAG: Enum = 'T'


class Modifier(models.Model):
    id: uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    faction: Faction = models.ForeignKey(Faction, on_delete=models.PROTECT)
    modifier_type: Enum = EnumField(enum=ModifierType, max_length=1)
    modifier_amount: int = models.IntegerField()

    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.faction}: +{self.modifier_amount}pts for {self.modifier_type}"
