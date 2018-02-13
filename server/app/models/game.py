import uuid

from django.db import models

from .managers import GameManager


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game_name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = GameManager()

    """
    todo: figure out how to start the weeklong at midnight and
    assign roles, assign roles, email players about what team they're on, etc.
    """

    def __str__(self):
        return self.game_name
