from django.db import models

from .game import Game
from .participant import Participant
from .user import User


class ModeratorManager(models.Manager):
    def create_moderator(self, user: User, game: Game, **extra_fields) -> 'Moderator':
        if user.participant(game):
            raise ValueError(f"The user {user} already exists in the game {game}.")

        moderator = self.model(user=user, game=game, **extra_fields)

        moderator.save()
        return moderator


class Moderator(Participant):
    character_name: str = models.CharField("Character name", max_length=180, blank=True, null=True)
    score: str = models.CharField("Moderator 'score'. Can include letters. For fun.", max_length=180, blank=True, null=True)

    objects = ModeratorManager()

    @property
    def is_moderator(self):
        return True

    def __str__(self):
        return self.character_name if self.character_name else self.user.get_full_name()
