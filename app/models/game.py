import uuid

from django.db import models


class GameManager(models.Manager):
    def create_game(self, name):
        game = self.model(name=name)
        game.save(using=self._db)
        return game


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game_name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = GameManager()

    def __str__(self):
        return self.game_name
