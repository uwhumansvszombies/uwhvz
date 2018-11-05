import uuid
from datetime import datetime

from django.db import models
from enumfields import Enum, EnumField

from .game import Game
from .participant import ParticipantRole
from .signup_location import SignupLocation
from .util import normalize_email


class SignupInviteManager(models.Manager):
    def create_signup_invite(self, game: Game, signup_location: SignupLocation, email: str,
                             participant_role: ParticipantRole = None) -> 'SignupInvite':
        email = normalize_email(email)
        signup_invite = self.model(
            game=game,
            signup_location=signup_location,
            email=email,
            participant_role=participant_role
        )
        signup_invite.save()
        return signup_invite


class SignupInvite(models.Model):
    id: uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    game: Game = models.ForeignKey(Game, on_delete=models.CASCADE)
    signup_location: SignupLocation = models.ForeignKey(SignupLocation, on_delete=models.CASCADE)
    email: str = models.EmailField()
    participant_role: Enum = EnumField(enum=ParticipantRole, max_length=1, blank=True, null=True)

    used_at: datetime = models.DateTimeField(null=True)
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    objects = SignupInviteManager()

    def __str__(self):
        return f"{self.game}: {self.email} at {self.signup_location}"
