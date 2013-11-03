#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bdosoa.settings')
    os.environ.setdefault('DJANGO_HOME', '/Users/andre/Downloads')
    os.environ.setdefault('DJANGO_DEBUG', '1')

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
