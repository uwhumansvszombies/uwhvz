import string
import random

from django.db import models


class PlayerManager(models.Manager):
    def create_player(self, user):
        code = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=6))

        # For set of all supply codes, each code must be unique
        while self.filter(code=code):
            code = ''.join(random.choices(
                string.ascii_uppercase + string.digits, k=6))

        player = self.model(user=user, code=code)
        player.save(using=self._db)
        return player
