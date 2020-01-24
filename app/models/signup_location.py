import uuid
from datetime import datetime

from django.db import models

from .game import Game


class SignupLocationManager(models.Manager):
    def create_signup_location(self, name: str, game: Game) -> 'SignupLocation':
        signup_location = self.model(name=name, game=game)
        signup_location.save()
        return signup_location


class SignupLocation(models.Model):
    id: uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game: Game = models.ForeignKey(Game, on_delete=models.PROTECT)
    name: str = models.CharField(max_length=150)

    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    mon_hours: str = models.CharField(max_length=15, null=True, blank=True)
    tues_hours: str = models.CharField(max_length=15, null=True, blank=True)
    wed_hours: str = models.CharField(max_length=15, null=True, blank=True)
    thurs_hours: str = models.CharField(max_length=15, null=True, blank=True)
    fri_hours: str = models.CharField(max_length=15, null=True, blank=True)

    objects = SignupLocationManager()

    def __str__(self):
        return self.name
