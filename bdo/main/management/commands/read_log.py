import logging

from django.core.management.base import BaseCommand
from optparse import make_option
from bdo.main import models


class Command(BaseCommand):
    help = 'Read XML log from MACP SPG'

    option_list = BaseCommand.option_list + (
        make_option('-d', '--debug', action='store_true', default=False,
                    help='increase logging verbosity'),
        make_option('-q', '--quiet', action='store_true', default=False,
                    help='reduce the logging verbosity'),
        make_option('-n', '--name', default='bdo-read_log',
                    help='name used for logging'),
    )

    def handle(self, *args, **options):

        # Configure logging
        log_format = \
            '%(asctime)s <%(name)s:%(levelname)s> %(message)s'

        logging.basicConfig(**{
            'level': (logging.DEBUG if options['debug'] else
                      logging.WARN if options['quiet'] else
                      logging.INFO),
            'format': log_format,
        })

        # Logger instance
        logger = logging.getLogger(options['name'])

        # Process log files
        for path in args:

            # Initialize XML string
            xml = ''

            # Read log file
            with open(path, 'r') as src:
                for line in src:

                    # New entry
                    if line.startswith('<<<') or line.startswith('>>>'):

                        # Process previous XML string if defined
                        if xml:
                            try:
                                msg = models.Message.from_string(xml)
                                msg.save()
                                print(msg)

                            except Exception as e:
                                logger.error(e)

                        # Start a new XML string
                        xml = line.split(' ', 1)[1]

                    # String continuation
                    else:

                        # Append to the current string
                        xml += line

                # Finished processing the file
                else:

                    # Process the last XML string
                    try:
                        msg = models.Message.from_string(xml)
                        print(msg)
                        #msg.save()

                    except Exception as e:
                        logger.error(e)
