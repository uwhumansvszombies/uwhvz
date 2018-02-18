from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r'^[\w.-]+$'
    message = _(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and ./-/_ characters.'
    )
    flags = 0
