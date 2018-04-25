import uuid

from django.db import models

from .user import User


class GameManager(models.Manager):
    def create_game(self, name):
        game = self.model(name=name)
        game.save()
        return game


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

    def __str__(self):
        return self.name
