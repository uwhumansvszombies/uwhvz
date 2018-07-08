from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from jinja2 import Environment
from svg.templatetags.svg import svg

from app.util import format_datetime


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
        'svg': svg,
    })
    env.filters.update({
        'format_datetime': format_datetime
    })
    return env
