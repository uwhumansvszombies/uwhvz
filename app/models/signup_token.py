import uuid

from django.db import models

from app.util import normalize_email
from .game import Game
from .signup_location import SignupLocation


class SignupTokenManager(models.Manager):
    def create_signup_token(self, game, signup_location, email):
        email = normalize_email(email)
        signup_location = self.model(game=game, signup_location=signup_location, email=email)
        signup_location.save()
        return signup_location


class SignupToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    signup_location = models.ForeignKey(SignupLocation, on_delete=models.CASCADE)
    email = models.EmailField()

    used_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = SignupTokenManager()

    def __str__(self):
        return f'{self.game}: {self.email} at {self.signup_location}'
