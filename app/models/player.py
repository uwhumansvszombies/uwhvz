import uuid
from datetime import datetime, timedelta

from django.db import transaction, models, DatabaseError
from enumfields import Enum, EnumField

from .faction import Faction
from .game import Game
from .modifier import Modifier, ModifierType
from .user import User
from .util import generate_code


class PlayerRole(Enum):
    HUMAN: Enum = 'H'
    ZOMBIE: Enum = 'Z'
    SPECTATOR: Enum = 'S'


class PlayerManager(models.Manager):
    def create_player(self, user: User, game: Game, role: PlayerRole, **extra_fields) -> 'Player':
        if user.player_set.filter(game=game, active=True).exists():
            raise ValueError(f"The user {user} already exists in the game {game}.")

        if 'code' in extra_fields:
            player = self.model(user=user, game=game, role=role, **extra_fields)
        else:
            code = generate_code(6)
            while self.filter(code=code):
                code = generate_code(6)
            player = self.model(user=user, game=game, role=role, code=code, **extra_fields)

        player.save()
        return player


class Player(models.Model):
    id: uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user: User = models.ForeignKey(User, on_delete=models.CASCADE)
    game: Game = models.ForeignKey(Game, on_delete=models.CASCADE)
    code: str = models.CharField(max_length=6)
    role: Enum = EnumField(enum=PlayerRole, max_length=1)

    active: bool = models.BooleanField(default=True)
    in_oz_pool: bool = models.BooleanField(default=False)

    faction: Faction = models.ForeignKey(Faction, on_delete=models.PROTECT, blank=True, null=True)
    point_modifier: int = models.IntegerField(default=0)

    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    objects = PlayerManager()

    def value(self, current_time: datetime) -> int:
        """
        Point value of a Human/Zombie player.
        Humans are worth 5 points as a kill, Zombies have their own scoring.
        """
        if self.is_human:
            return 5
        eight_hours_ago = current_time - timedelta(hours=8)
        return max(0, 5 - self.receiver_tags
                   .filter(tagged_at__gte=eight_hours_ago, tagged_at__lt=current_time, active=True)
                   .count())

    def score(self) -> int:
        """
        Individual score of a player.
        """
        total_score = self.point_modifier
        for tag in self.initiator_tags.filter(active=True).all():
            total_score += tag.receiver.value(tag.tagged_at) + tag.point_modifier

        for code in self.supplycode_set.all():
            total_score += code.value + code.point_modifier

        faction_score_modifiers = Modifier.objects.filter(faction=self.faction,
                                                          modifier_type=ModifierType.ONE_TIME_USE).all()
        for faction_point_modifier in faction_score_modifiers:
            total_score += faction_point_modifier.modifier_amount

        return total_score

    def kill(self) -> 'Player':
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
    def is_spectator(self) -> bool:
        return self.role == PlayerRole.SPECTATOR

    @property
    def is_zombie(self) -> bool:
        return self.role == PlayerRole.ZOMBIE

    @property
    def is_human(self) -> bool:
        return self.role == PlayerRole.HUMAN

    @property
    def has_faction(self) -> bool:
        return self.faction is not None

    def __str__(self):
        return self.user.get_full_name()
