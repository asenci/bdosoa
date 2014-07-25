"""
bdosoa - helper functions
"""

import cherrypy
import logging
import string

from random import SystemRandom


def gen_token(size=32):
    """Generate random tokens

    :param int size: Size of the generated token
    :return: A random token
    :rtype: str
    """

    charlist = string.digits + string.letters

    token = [SystemRandom().choice(charlist) for _ in range(size)]

    return ''.join(token)


def config_logging(name):
    """Configure logging for modules outside CherryPy

    :param str name: Logger name
    """

    # Get CherryPy builtin handlers
    cherrypy_log_handlers = [
        cherrypy.log._get_builtin_handler(cherrypy.log.error_log, h)
        for h in ['screen', 'file', 'wsgi']
    ]

    logger = logging.getLogger(name)
    logger.setLevel(cherrypy.log.error_log.getEffectiveLevel())

    for handler in cherrypy_log_handlers:
        if handler is not None:
            logger.addHandler(handler)
