import uuid
from datetime import timedelta

from django.db import models
from enumfields import Enum, EnumField

from app.accounts import User
from .game import Game


class Player(models.Model):
    class Role(Enum):
        HUMAN = 'H'
        ZOMBIE = 'Z'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)
    role = EnumField(enum=Role, max_length=1)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def value(self, at):
        """
        Point value of a Human/Zombie player.
        Humans are worth 5 points as a kill, Zombies have their own scoring.
        """
        if self.role == Player.Role.HUMAN:
            return 5
        eight_hours_ago = at - timedelta(hours=8)
        return max(0, 5 - self.receiver_tags
                   .filter(tagged_at__gte=eight_hours_ago, tagged_at__lt=at)
                   .count())

    def score(self):
        """
        Individual score of a player.
        """
        total_score = 0
        for tag in self.initiator_tags.all():
            total_score += tag.receiver.value(tag.tagged_at)
        return total_score

    def __str__(self):
        return self.user.get_full_name()
