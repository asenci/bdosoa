import logging

from django.core.management.base import BaseCommand
from optparse import make_option

from bdo.main import xml
from bdo.main.models import Message


class Command(BaseCommand):
    help = 'Import XML log from MACP SPG'

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
        self.logger = logging.getLogger(options['name'])

        # Process log files
        for path in args:

            # Initialize XML string
            xml_str = ''

            # Read log file
            with open(path, 'r') as src:
                for line in src:

                    # New entry
                    if line.startswith('<<<') or line.startswith('>>>'):

                        # Process previous XML string if defined
                        if xml_str:
                            self.proc_xml(xml_str)

                        # Start a new XML string
                        xml_str = line.split(' ', 1)[1]

                    # String continuation
                    else:

                        # Append to the current string
                        xml_str += line

                # Finished processing the file
                else:

                    # Process the last XML string
                    self.proc_xml(xml_str)

    def proc_xml(self, xml_str):
        try:
            xml_obj = xml.from_string(xml_str)
            msg = Message.from_xml(xml_obj, xml_str)
            msg.save()
            self.logger.info(msg)

        except Exception as e:
            self.logger.error(e)
