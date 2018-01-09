import uuid

from django.db import models


class GameManager(models.Manager):
    def create_game(self, name):
        game = self.model(name=name)

        game.save(using=self._db)
        return game


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(default='UW HvZ Weeklong', max_length=100)
    is_active = models.BooleanField(default=False)
    is_started = models.BooleanField(default=False)

    games = GameManager()

    # for signup periods
    def activate(self):
        self.is_active = True

    """
    for starting the weeklong at midnight and assigning roles, etc
    todo: assign roles, email players about what team they're on
    """
    def start(self):
        self.is_started = True

    def __str__(self):
        return self.name
