import uuid
from datetime import datetime

from django.db import models

from .user import User


class LegacyManager(models.Manager):
    def create_legacy(self, user: User, value: int, details: str) -> 'Legacy':
        legacy = self.model(user=user, value=value, details=details)
        legacy.save()
        return legacy


class Legacy(models.Model):
    # This model is used to store gains or losses of legacy points
    # If a player has no legacys, they have a value of zero implicitly
    
    id: uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value: int = models.IntegerField()
    
    # this is the amount gained or lost by the user
    # a negative value implies losing points, a positive value implies gaining points
    
    details: str = models.CharField(max_length=50)
    
    user: User = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_legacy')
    

    time: datetime = models.DateTimeField(auto_now_add=True)
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    objects = LegacyManager()

    def __int__(self):
        return self.value
