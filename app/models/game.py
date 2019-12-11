import uuid
from datetime import datetime
from pytz import utc
from enum import Enum, auto

from django.db import models

from .user import User


class GameManager(models.Manager):
    def create_game(self, name: str, **kwargs) -> 'Game':
        game = self.model(name=name, **kwargs)
        game.save()
        return game


class GameState(Enum):
    """
    The three states a game can take.
    SIGNUPS: when a game has been created but has not started yet; a game in its signup period.
    RUNNING: when a game has been created and has started; a game that's started.
    FINISHED: when a game has ended; a past/previous game.
    """
    SIGNUPS = auto()
    RUNNING = auto()
    FINISHED = auto()


class Game(models.Model):
    id: uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name: str = models.CharField(max_length=100, unique=True)

    started_on: datetime = models.DateTimeField(null=True, blank=True)
    started_by: User = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='started_games',
        null=True,
        blank=True
    )

    ended_on: datetime = models.DateTimeField(null=True, blank=True)
    ended_by: User = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ended_games',
        null=True,
        blank=True
    )

    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    objects = GameManager()

    def state(self) -> Enum:
        if self.started_on < utc.localize(datetime.now()):
            return GameState.FINISHED if self.ended_on else GameState.RUNNING
        else:
            return GameState.SIGNUPS

    @property
    def is_signups(self) -> bool:
        return self.state() == GameState.SIGNUPS

    @property
    def is_running(self) -> bool:
        return self.state() == GameState.RUNNING

    @property
    def is_finished(self) -> bool:
        return self.state() == GameState.FINISHED

    def __str__(self):
        return self.name
