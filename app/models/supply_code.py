import random
import string
import uuid

from django.db import models

from .player import Player


class SupplyCodeManager(models.Manager):
    def create_supply_code(self):
        code = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=6))

        # For set of all supply codes, each code must be unique
        while self.filter(code=code):
            code = ''.join(random.choices(
                string.ascii_uppercase + string.digits, k=6))

        supply_code = self.model(code=code)
        supply_code.save(using=self._db)
        return supply_code


class SupplyCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=6, unique=True)
    value = models.IntegerField()
    claimed_by = models.ForeignKey(Player, on_delete=models.CASCADE)
    claimed_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = SupplyCodeManager()
