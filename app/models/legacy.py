import uuid
from datetime import datetime

from django.db import models

from .user import User


class LegacyManager(models.Manager):
    def create_legacy(self, user: User, cost: int, details: str) -> 'Legacy':
        legacy = self.model(user=user, cost=cost, details=details)
        legacy.save()
        return legacy


class Legacy(models.Model):
    id: uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cost: int = models.IntegerField()
    details: str = models.CharField(max_length=50)
    
    user: User = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_name')
    

    time: datetime = models.DateTimeField(auto_now_add=True)
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    objects = LegacyManager()

    def __int__(self):
        return self.cost