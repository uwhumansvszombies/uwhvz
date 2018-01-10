import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .user_validator import UsernameValidator


class User(AbstractUser):
    username_validator = UsernameValidator()

    username = models.CharField(
        max_length=150,
        unique=True,
        help_text=_('You need a username so we can identify you. Must be 150 characters or fewer, containing any of letters, numbers, periods (.), dashes (-), or underscores (_).'),
        validators=[username_validator],
        error_messages={
            'unique': _("An account with that username already exists."),
        },
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(_('first name'), max_length=100, blank=False)
    last_name = models.CharField(_('last name'), max_length=100, blank=False)
    email = models.EmailField(
        _('email address'), 
        unique=True,
        help_text=_('Please enter a valid email address - we promise not to spam your inbox!'),
        error_messages={
            'unique': _("An account with that email address already exists."),
        },
    )

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
