import uuid

from django.db import models


class SignupLocationManager(models.Manager):
    def create_signup_location(self, name):
        signup_location = self.model(name=name)
        signup_location.save()
        return signup_location


class SignupLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = SignupLocationManager()

    def __str__(self):
        return self.name
