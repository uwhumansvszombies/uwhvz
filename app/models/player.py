import uuid
from datetime import timedelta

from django.db import transaction, models, DatabaseError
from enumfields import Enum, EnumField

from app.models.util import generate_code
from .faction import Faction
from .game import Game
from .user import User


class PlayerManager(models.Manager):
    def create_player(self, user, game, role, **extra_fields):
        if user.player_set.filter(game=game, active=True).exists():
            raise ValueError(f'The user {user} already exists in the game {game}.')

        if 'code' in extra_fields:
            player = self.model(user=user, game=game, role=role, **extra_fields)
        else:
            code = generate_code(6)
            while self.filter(code=code):
                code = generate_code(6)
            player = self.model(user=user, game=game, code=code, role=role, **extra_fields)

        player.save()
        return player


class PlayerRole(Enum):
    HUMAN = 'H'
    ZOMBIE = 'Z'
    SPECTATOR = 'S'


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    role = EnumField(enum=PlayerRole, max_length=1)
    in_oz_pool = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    faction = models.ForeignKey(Faction, on_delete=models.PROTECT, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = PlayerManager()

    def value(self, at):
        """
        Point value of a Human/Zombie player.
        Humans are worth 5 points as a kill, Zombies have their own scoring.
        """
        if self.is_human:
            return 5
        eight_hours_ago = at - timedelta(hours=8)
        return max(0, 5 - self.receiver_tags
                   .filter(tagged_at__gte=eight_hours_ago, tagged_at__lt=at, active=True)
                   .count())

    def score(self):
        """
        Individual score of a player.
        """
        total_score = 0
        for tag in self.initiator_tags.filter(active=True).all():
            total_score += tag.receiver.value(tag.tagged_at) + tag.modifier

        for code in self.supplycode_set.all():
            total_score += code.value + code.modifier

        return total_score

    def kill(self):
        if self.is_zombie:
            raise ValueError("This player is already a zombie.")

        self.active = False
        try:
            with transaction.atomic():
                self.save()
                return Player.objects.create_player(
                    self.user, self.game, PlayerRole.ZOMBIE, code=self.code)
        except DatabaseError:
            self.active = True

    @property
    def is_spectator(self):
        return self.role == PlayerRole.SPECTATOR

    @property
    def is_zombie(self):
        return self.role == PlayerRole.ZOMBIE

    @property
    def is_human(self):
        return self.role == PlayerRole.HUMAN

    def __str__(self):
        return self.user.get_full_name()
