"""Django settings module"""
import os


RUNDIR = os.environ.get('DJANGO_HOME', '')

ADMINS = MANAGERS = (
    ('NOC', 'noc@enterchip.com.br')
)

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(RUNDIR, 'database', 'main.db'),
    },
}

DEBUG = TEMPLATE_DEBUG = os.environ.get('DJANGO_DEBUG', False)

EMAIL_HOST = 'smtp.gtitelecom.net.br'

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

MEDIA_ROOT = os.path.join(RUNDIR, 'media')

MEDIA_URL = '/media/'

ROOT_URLCONF = 'bdosoa.main.urls'

SECRET_KEY = ';UgDHSv1xUpZPOoSTVTwR#8zG_5)]uMS2cXMcpM-rhTox&4r6-gyuVj71HsYn0zJ'

STATIC_ROOT = os.path.join(RUNDIR, 'static')

STATIC_URL = '/static/'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True
