import uuid
from datetime import datetime
from typing import Union

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email: str, password: str, **extra_fields) -> 'User':
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email: str = None, password: str = None, **extra_fields) -> 'User':
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields) -> 'User':
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff = True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser = True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    A custom User model which looks very similar to AbstractUser with the
    username field removed.

    Email and password are required. Other fields are optional.
    """
    id: uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name: str = models.CharField("First name", max_length=30, blank=True)
    last_name: str = models.CharField("Last name", max_length=150, blank=True)
    email: str = models.EmailField(
        "Email address",
        unique=True,
        help_text="Please enter a valid email address.",
        error_messages={
            'unique': "An account with that email address already exists.",
        },
    )
    is_staff: bool = models.BooleanField(
        "Staff status",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_active: bool = models.BooleanField(
        "Active",
        default=True,
        help_text="Designates whether this user should be treated as active. "
                  "Deselect this instead of deleting accounts."
    )

    date_joined: datetime = models.DateTimeField("Date joined", default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def clean(self) -> None:
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self) -> str:
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self) -> str:
        return self.first_name

    def email_user(self, subject: str, message: str, from_email: str = None, **kwargs) -> None:
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def is_moderator(self) -> bool:
        return self.participant.is_moderator or self.is_staff

    @property
    def is_volunteer(self) -> bool:
        return self.groups.filter(name='Volunteers').exists() or self.is_staff

    def participant(self, game: 'Game') -> Union['Player', 'Spectator', 'Moderator', None]:
        if self.player_set.filter(game=game, active=True).exists():
            return self.player_set.get(game=game, active=True)
        elif self.spectator_set.filter(game=game, active=True).exists():
            return self.spectator_set.get(game=game, active=True)
        elif self.moderator_set.filter(game=game, active=True).exists():
            return self.moderator_set.get(game=game, active=True)
        else:
            return None
