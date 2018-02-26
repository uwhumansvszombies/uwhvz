import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core import validators
from django.utils.deconstruct import deconstructible


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r'^[\w.-]+$'
    message = _(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and ./-/_ characters.'
    )
    flags = 0


class User(AbstractUser):
    username_validator = UsernameValidator()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text=_('You need a username so we can identify you. Maximum 150 characters, containing '
                    'any letters, numbers, periods (.), dashes (-), or underscores (_).'),
        validators=[username_validator],
        error_messages={
            'unique': _("An account with that username already exists."),
        },
    )
    first_name = models.CharField(_('First name'), max_length=100, blank=False)
    last_name = models.CharField(_('Last name'), max_length=100, blank=False)
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Please enter a valid email address - we promise not to spam your inbox!'),
        error_messages={
            'unique': _("An account with that email address already exists."),
        },
    )

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']


class UserModelBackend():
    def authenticate(self, username=None, password=None):
        if '@' in username:
            kwargs = { 'email': username }
        else:
            kwargs = { 'username': username }
        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
