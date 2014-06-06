def gen_token(size=32):
    """Generate random tokens"""
    from random import SystemRandom
    from string import digits, letters

    charlist = letters + digits

    token = [SystemRandom().choice(charlist) for _ in range(size)]

    return ''.join(token)


def config_logging(name):
    """Configure logging for modules outside CherryPy"""
    import cherrypy
    import logging

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
