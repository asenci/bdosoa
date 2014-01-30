import logging
import uwsgi

from threading import Event, Thread

from bdosoa.main.models import QueuedMessage, QueuedSync


def loop(cmd, event):
    count = 0
    event.set()

    logger.debug('Starting thread for "{0}"'.format(cmd))
    while event.is_set():
        count += 1
        logger.debug('Running task for "{0}" [{1}]'.format(cmd, count))
        event.clear()

        if cmd == 'flush_messages_queue':
            QueuedMessage.flush()

        if cmd == 'flush_sync_queue':
            QueuedSync.flush()

    else:
        logger.debug('Finished thread for "{0}"'.format(cmd))


if __name__ == '__main__':
    logger = logging.getLogger('bdosoa.uwsgi_mule')
    logger.info('Starting uWSGI mule')

    try:
        threads = {}
        run_again = Event()

        while True:
            msg = uwsgi.mule_get_msg()
            logger.debug('Received message: {0!r}'.format(msg))

            t = threads.get(msg, None)
            if t is not None and t.is_alive():
                logger.debug('Thread for "{0}" is still running'.format(msg))
                run_again.set()

            else:
                threads[msg] = Thread(target=loop, args=[msg, run_again])
                threads[msg].start()

    except Exception as e:
        logger.exception(e)
