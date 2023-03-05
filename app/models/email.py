import uuid
from datetime import datetime

from django.db import models
from enumfields import Enum, EnumField

from .game import Game

class RecipientGroup(Enum):
    HUMAN = 'H'
    ZOMBIE = 'Z'
    ALL = 'A'
    VOLUNTEER = 'V'
    USER = "U"

class EmailManager(models.Manager):
    def create_email(self, name: str, data : str, group: RecipientGroup, game: Game, **extra_fields) -> 'Email':
        email = self.model(name=name, data=data, group=group, game=game, **extra_fields)
        email.save()
        return email


class Email(models.Model):
    id: uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game: Game = models.ForeignKey(Game, on_delete=models.PROTECT)
    name: str = models.CharField(max_length=256)
    data: str = models.TextField(blank=True)
    group: Enum = EnumField(enum=RecipientGroup, max_length=1)
    player_made: bool = models.BooleanField(default=False)
    visible: bool = models.BooleanField(default=True)
    target_player_code: str = models.CharField(default="", max_length=256)  # target_player code when group is 'User'

    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    objects = EmailManager()

    def __str__(self):
        return self.name
