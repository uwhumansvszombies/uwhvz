import uuid

from django.db import models

from .managers import TagManager
from .player import Player


class Tag(models.Model):
    """
    A tag is defined as an "initiator" who has tagged a "receiver".
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    initiator = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='initiator_tags'
    )
    receiver = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='receiver_tags'
    )
    tagged_at = models.DateTimeField()
    location = models.CharField(blank=True, max_length=100)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = TagManager()

    def __str__(self):
        return f'{self.initiator} ({self.initiator.role}) --> ' + \
               f'{self.receiver} ({self.receiver.role})'
