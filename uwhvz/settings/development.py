from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6e4#bj2ea@i)f*xj4ht6rrthq@f3vw9(v8az+9==pf+3ys8pb!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

COMPRESS_OFFLINE = True

ALLOWED_HOSTS = ['*']

SITE_URL = 'http://127.0.0.1:8000'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
