import uuid

from django.db import models
from enumfields import Enum, EnumField

from .faction import Faction


class ModifierType(Enum):
    SUPPLY_CODE = 'S'
    TAG = 'T'


class Modifier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    faction = models.ForeignKey(Faction, on_delete=models.PROTECT)
    modifier_type = EnumField(enum=ModifierType, max_length=1)
    modifier_amount = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.faction} +{self.modifier_amount} for {self.modifier_type}'
