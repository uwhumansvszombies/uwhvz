import uuid

from django.db import models
from enumfields import EnumField

from app.util import normalize_email
from . import Game, PlayerRole, SignupLocation


class SignupInviteManager(models.Manager):
    def create_signup_invite(self, game, signup_location, email, player_role=None):
        email = normalize_email(email)
        signup_invite = self.model(game=game, signup_location=signup_location, email=email, player_role=player_role)
        signup_invite.save()
        return signup_invite


class SignupInvite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    signup_location = models.ForeignKey(SignupLocation, on_delete=models.CASCADE)
    email = models.EmailField()
    player_role = EnumField(enum=PlayerRole, max_length=1, blank=True, null=True)

    used_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = SignupInviteManager()

    def __str__(self):
        return f'{self.game}: {self.email} at {self.signup_location}'
