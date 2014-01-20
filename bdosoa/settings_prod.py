from bdosoa.settings import *

ADMINS = MANAGERS = (
    ('NOC', 'noc@enterchip.com.br')
)

DEFAULT_FROM_EMAIL = SERVER_EMAIL = 'webmaster@gtitelecom.net.br'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gtitelecom.net.br'
#EMAIL_HOST_USER =
#EMAIL_HOST_PASSWORD =
#EMAIL_PORT = 587
#EMAIL_USE_TLS = True

SECRET_KEY = environ.get('DJANGO_SECRET', SECRET_KEY)
