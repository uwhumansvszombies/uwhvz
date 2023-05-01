import os

from django.contrib.messages import constants as messages

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

MEDIA_DIR = os.path.join(BASE_DIR, 'media')
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

INSTALLED_APPS = [
    'app',
    'django_su',  # must be before ``django.contrib.admin``    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sass_processor',
    'compressor',
    'svg',
    'django_user_agents',
    'rest_framework',
    'rest_auth',
    'modelcluster',
    'taggit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]

ROOT_URLCONF = 'uwhvz.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [os.path.join(BASE_DIR, 'app', 'templates', 'jinja2')],
        'APP_DIRS': False,
        'OPTIONS': {
            'environment': 'uwhvz.jinja2.environment',
            'extensions': [
                'sass_processor.jinja2.ext.SassSrc',
                'compressor.contrib.jinja2ext.CompressorExtension',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_su.context_processors.is_su',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'uwhvz.wsgi.application'

USER_AGENTS_CACHE = 'default'

#************

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
	'applogfile': {
        'level':'DEBUG',
        'class':'logging.handlers.RotatingFileHandler',
        'filename': os.path.join(BASE_DIR, 'uwhvz.log'),
        'maxBytes': 1024*1024*15, # 15MB
        'backupCount': 10,
    	},
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
	'uwhvz': {
            'handlers': ['applogfile',],
            'level': 'DEBUG',
        },
    }
}

#************

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []

AUTH_USER_MODEL = 'app.User'

AUTHENTICATION_BACKENDS = (
    'django_su.backends.SuBackend',
    'django.contrib.auth.backends.ModelBackend',
)

#WAGTAIL_FRONTEND_LOGIN_URL = '/accounts/login'
LOGIN_REDIRECT_URL = '/dashboard/player'
LOGOUT_REDIRECT_URL = '/'

ATOMIC_REQUESTS = True

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = STATIC_DIR
MEDIA_URL = '/media/'
MEDIA_ROOT = MEDIA_DIR

STATICFILES_FINDERS = [
#    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
    'compressor.finders.CompressorFinder',
]

WAGTAIL_SITE_NAME = 'UW Humans vs Zombies'

SASS_PRECISION = 8
SASS_OUTPUT_STYLE = 'compact'
SASS_PROCESSOR_ENABLED = True

MESSAGE_TAGS = {
    messages.DEBUG: 'dark',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# If set to True then user signups will be restricted to those who have a signup token.
# If set to False then users will be able to signup freely without token.
TOKEN_RESTRICTED_SIGNUPS = False
