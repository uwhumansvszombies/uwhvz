import uuid

from enum import Enum, auto
from django.db import models

from .user import User


class GameManager(models.Manager):
    def create_game(self, name, **kwargs):
        game = self.model(name=name, **kwargs)
        game.save()
        return game


class GameState(Enum):
    ACTIVE = auto()
    RUNNING = auto()
    FINISHED = auto()


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    started_on = models.DateTimeField(null=True, blank=True)
    started_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='started_games', null=True, blank=True)

    ended_on = models.DateTimeField(null=True, blank=True)
    ended_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ended_games', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = GameManager()

    def state(self):
        if self.started_on:
            return GameState.FINISHED if self.ended_on else GameState.RUNNING
        else:
            return GameState.ACTIVE
    
    @property
    def is_active(self):
        return self.state() == GameState.ACTIVE

    @property
    def is_running(self):
        return self.state() == GameState.RUNNING

    @property
    def is_finished(self):
          return self.state() == GameState.FINISHED

    def __str__(self):
        return self.name
