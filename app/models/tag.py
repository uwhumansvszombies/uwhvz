import uuid
from datetime import datetime

from django.db import models, transaction

from .player import Player


class TagManager(models.Manager):
    def create_tag(self, initiator: Player, receiver: Player, tagged_at: datetime, location: str, description: str, point_modifier: int = 0) -> 'Tag':

        if initiator.role == receiver.role:
            tag_type = "stuns" if initiator.is_human else "tags"
            raise ValueError(f"You cannot report {tag_type} on players of the same team as you.")
        if initiator.game != receiver.game:
            raise ValueError("A stun/tag must be between two players in the same game.")

        with transaction.atomic():
            tag = self.model(
                initiator=initiator,
                receiver=receiver,
                tagged_at=tagged_at,
                location=location,
                description=description,
                point_modifier=point_modifier,
            )
            tag.save()
            if receiver.is_human:
                receiver.kill()
        return tag


class Tag(models.Model):
    """
    A tag is defined as an "initiator" who has tagged a "receiver".
    """
    id: uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    initiator: Player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='initiator_tags')
    receiver: Player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='receiver_tags')
    tagged_at: datetime = models.DateTimeField()
    location: str = models.CharField(blank=True, max_length=100)
    description: str = models.TextField(blank=True)

    # If the active property is set to False, then this tag is ignored.
    active: bool = models.BooleanField(default=True)
    point_modifier: int = models.IntegerField(default=0)

    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    objects = TagManager()

    def __str__(self):
        initiator = self.initiator
        receiver = self.receiver
        return f"{initiator} ({initiator.role}) → {receiver} ({receiver.role})"
