import logging
import uwsgi

from bdosoa.main.models import QueuedMessage

if __name__ == '__main__':
    logger = logging.getLogger('bdosoa.uwsgi_mule')
    logger.info('Starting uWSGI mule')

    try:
        while True:
            cmd = uwsgi.mule_get_msg()
            logger.debug('Received command: {0!r}'.format(cmd))

            if cmd == 'flush_queue':
                QueuedMessage.flush()

    except Exception as e:
        logger.exception(e)
