import uuid

from django.db import models

from .player import Player


class TagManager(models.Manager):
    def create_tag(self, initiator, receiver, time_tagged, location, description):
         # validate that this is a valid tag. I.e. initiator.role != receiver.role
        tagged_at = time_tagged

        tag = self.model(initiator=initiator,
                         receiver=receiver,
                         tagged_at=tagged_at,
                         location=location,
                         description=description)
        return tag


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
    location = models.CharField(blank=True, max_length=100)
    description = models.TextField(blank=True)

    tags = TagManager()

    def __str__(self):
        return f'{self.initiator} ({self.initiator.role}) --> ' + \
               f'{self.receiver} ({self.receiver.role})'
