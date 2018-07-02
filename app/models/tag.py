import uuid
from datetime import datetime

from django.db import models, transaction

from .player import Player, PlayerRole


class TagManager(models.Manager):
    def create_tag(self, initiator: Player, receiver: Player, tagged_at: datetime, location: str, description: str):
        if initiator.role == receiver.role:
            raise ValueError('A tag must be between a human and a zombie.')
        if initiator.game != receiver.game:
            raise ValueError('A tag must be between two players in the same game.')

        with transaction.atomic():
            tag = self.model(
                initiator=initiator,
                receiver=receiver,
                tagged_at=tagged_at,
                location=location,
                description=description,
            )
            tag.save()
            if receiver.role == PlayerRole.HUMAN:
                receiver.kill()
        return tag


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

    # If active is False this tag is ignored.
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = TagManager()

    def __str__(self):
        initiator = self.initiator
        receiver = self.receiver
        return f'{initiator} ({initiator.role}) --> {receiver} ({receiver.role}) at {self.tagged_at}'
