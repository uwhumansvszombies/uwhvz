import uuid

from django.db import models

from .player import Player


class Tag(models.Model):
    """
    A tag is defined as an "initiator" who has tagged a "receiver".
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    initiator = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='initiator_tags')
    receiver = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='receiver_tags')
    tagged_at = models.DateTimeField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.initiator} ({self.initiator.role}) --> ' + \
               f'{self.receiver} ({self.receiver.role})'
