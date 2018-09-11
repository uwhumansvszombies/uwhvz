from django.db import models

from .game import Game
from .participant import Participant
from .user import User


class SpectatorManager(models.Manager):
    def create_spectator(self, user: User, game: Game, **extra_fields) -> 'Spectator':
        if user.participant_set.filter(game=game, active=True).exists():
            raise ValueError(f"The user {user} already exists in the game {game}.")

        spectator = self.model(user=user, game=game, **extra_fields)
        spectator.save()
        return spectator


class Spectator(Participant):
    participant = models.OneToOneField(Participant, parent_link=True, on_delete=models.CASCADE, primary_key=True)

    objects = SpectatorManager()
