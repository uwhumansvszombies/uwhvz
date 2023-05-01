from .common import *

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False
ALLOWED_HOSTS = ['*']
SITE_URL = 'https://uwhvz.uwaterloo.ca'

ADMINS = [
    ('UW HvZ', 'uwhumansvszombies@gmail.com'),
    ('Jake Rempel', 'jake.rem@telus.net')
]

SERVER_EMAIL = 'uwhumansvszombies@gmail.com'
DEFAULT_FROM_EMAIL = 'uwhumansvszombies@gmail.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True

## GMAIL CONNECTION
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'uwhumansvszombies@gmail.com'
EMAIL_HOST_PASSWORD = os.environ['GMAIL_PASSWORD']
EMAIL_PORT = 587

## MAILJET CONNECTION
#EMAIL_HOST = 'in-v3.mailjet.com'
#EMAIL_HOST_USER = # THIS IS DEPRECATED 
#EMAIL_HOST_PASSWORD = # THIS IS DEPRECATED 
#EMAIL_PORT = 587

# MAILCHIMP CREDENTIALS
MAILCHIMP_API_KEY = os.environ['MAILCHIMP_API'] 
MAILCHIMP_DATA_CENTER = "us16"
MAILCHIMP_EMAIL_LIST_ID = "3fb33ac197"

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
