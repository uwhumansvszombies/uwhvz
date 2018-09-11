import uuid
from datetime import datetime

from django.db import models
from enumfields import Enum
from model_utils.managers import InheritanceManager

from .game import Game
from .user import User


class ParticipantRole(Enum):
    HUMAN: Enum = 'H'
    ZOMBIE: Enum = 'Z'
    SPECTATOR: Enum = 'S'
    MODERATOR: Enum = 'M'


class Participant(models.Model):
    id: uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user: User = models.ForeignKey(User, on_delete=models.CASCADE)
    game: Game = models.ForeignKey(Game, on_delete=models.CASCADE)
    active: bool = models.BooleanField(default=True)

    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    objects = InheritanceManager()

    class Meta:
        base_manager_name = 'objects'

    @property
    def type(self):
        return self.__class__.__name__

    def __str__(self):
        return self.user.get_full_name()
