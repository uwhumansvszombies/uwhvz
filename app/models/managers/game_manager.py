from django.db import models


class GameManager(models.Manager):
    def create_game(self, name):
        game = self.model(name=name)
        game.save(using=self._db)
        return game
