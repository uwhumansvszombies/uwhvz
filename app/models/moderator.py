from django.db import models

from .game import Game
from .participant import Participant
from .user import User


class ModeratorManager(models.Manager):
    def create_moderator(self, user: User, game: Game, **extra_fields) -> 'Moderator':
        if user.participant_set.filter(game=game, active=True).exists():
            raise ValueError(f"The user {user} already exists in the game {game}.")

        moderator = self.model(user=user, game=game, **extra_fields)
        moderator.save()
        return moderator


class Moderator(Participant):
    participant = models.OneToOneField(Participant, parent_link=True, on_delete=models.CASCADE, primary_key=True)

    objects = ModeratorManager()
