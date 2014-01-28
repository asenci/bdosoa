"""Django settings module"""
from os import environ, path

DEBUG = TEMPLATE_DEBUG = environ.get('DJANGO_DEBUG', '1') == '1'
DJANGO_HOME = environ.get('DJANGO_HOME', '')

ADMINS = (
    ('NOC', 'noc@enterchip.com.br')
)

ALLOWED_HOSTS = ['.gtitelecom.net.br']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(DJANGO_HOME, 'default.db'),
        'CONN_MAX_AGE': None,
    },
}

DEFAULT_FROM_EMAIL = SERVER_EMAIL = 'webmaster@gtitelecom.net.br'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' \
    if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gtitelecom.net.br'
#EMAIL_HOST_USER =
#EMAIL_HOST_PASSWORD =
#EMAIL_PORT = 587
EMAIL_SUBJECT_PREFIX = '[bdosoa] '
#EMAIL_USE_TLS = True

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'bdosoa.main',
)

LANGUAGE_CODE = 'pt-br'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },

    'formatters': {
        'default': {
            'format': '%(asctime)s <%(name)s:%(levelname)s> %(message)s'
        },
        'debug': {
            'format': '%(asctime)s <%(name)s:%(levelname)s>'
                      ' [%(module)s:%(process)d:%(thread)d] %(message)s'
        },
    },

    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'default': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'debug' if DEBUG else 'default',
            'filename': path.join(DJANGO_HOME, 'bdosoa.log'),
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },

    'loggers': {
        'bdosoa': {
            'handlers': ['console', 'default'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
        'django': {
            'handlers': ['console', 'default'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'py.warnings': {
            'handlers': ['console'],
        },
    },
}

MEDIA_ROOT = path.join(DJANGO_HOME, 'media')

MEDIA_URL = '/media/'

ROOT_URLCONF = 'bdosoa.main.urls'

SECRET_KEY = environ.get(
    'DJANGO_SECRET',
    ';UgDHSv1xUpZPOoSTVTwR#8zG_5)]uMS2cXMcpM-rhTox&4r6-gyuVj71HsYn0zJ'
)

STATIC_ROOT = path.join(DJANGO_HOME, 'static')

STATIC_URL = '/static/'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True
