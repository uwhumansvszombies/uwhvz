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

    games = GameManager()

    """
    todo: figure out how to start the weeklong at midnight and
    assign roles, assign roles, email players about what team they're on, etc.
    """

    def __str__(self):
        return self.name
