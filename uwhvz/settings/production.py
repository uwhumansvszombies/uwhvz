from .common import *

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False
ALLOWED_HOSTS = ['*']
SITE_URL = 'https://uwhvz.uwaterloo.ca'

ADMINS = [
    ('Tristan Ohlson', 'tsohlson@gmail.com'),
    ('Tiffany Yeung', 'tiffanynwyeung@gmail.com'),

]

SERVER_EMAIL = 'uwaterloohumansvszombies@gmail.com'
DEFAULT_FROM_EMAIL = 'uwaterloohumansvszombies@gmail.com'
EMAIL_BACKEND = 'post_office.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'uwaterloohumansvszombies@gmail.com'
EMAIL_HOST_PASSWORD = os.environ['EMAIL_PASSWORD']
EMAIL_PORT = 587

POST_OFFICE = {
    'BATCH_SIZE': 5,  # Max batch to send at a time
    'LOG_LEVEL': 2,  # Log fails and successes
    'BACKENDS': {
        'default': 'django.core.mail.backends.smtp.EmailBackend'
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

COMPRESS_OFFLINE = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}

# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_HSTS_SECONDS = 60
# SECURE_HSTS_PRELOAD = True
# X_FRAME_OPTIONS = 'DENY'
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
