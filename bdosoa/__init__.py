# Force Django environment setup

# noinspection PyUnresolvedReferences
from django.test import Client
Client().get('/admin/')
