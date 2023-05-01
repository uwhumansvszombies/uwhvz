import uuid
from datetime import datetime

from django.db import models
from enumfields import Enum, EnumField

from .faction import Faction


class ModifierType(Enum):
    ONE_TIME_USE = 'O'
    SUPPLY_CODE = 'S'
    TAG = 'T'

class ModifierManager(models.Manager):
    def create_modifier(self, faction: Faction, modifier_type: ModifierType, modifier_amount: int) -> "Modifier":
        modifier = self.model(faction=faction, modifier_type=modifier_type, modifier_amount=modifier_amount)
        modifier.save()

        return modifier


class Modifier(models.Model):
    id: uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    faction: Faction = models.ForeignKey(Faction, on_delete=models.PROTECT)
    modifier_type: Enum = EnumField(enum=ModifierType, max_length=1)
    modifier_amount: int = models.IntegerField()

    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)
    
    objects = ModifierManager()

    def __str__(self):
        return f"{self.faction}: +{self.modifier_amount}pts for {self.modifier_type}"

    def detail(self):
        return f"+{self.modifier_amount} points for {self.modifier_type}"
