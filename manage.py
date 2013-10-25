#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bdo.settings")
    os.environ.setdefault('DJANGO_DEBUG', '1')
    os.environ.setdefault(
        'DJANGO_HOME', os.path.join(os.path.dirname(__file__), 'run'))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
