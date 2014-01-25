import logging
import libspg
import libspg.bdo

from django.core.management.base import BaseCommand
from django.utils.timezone import utc

from bdosoa.main.models import Message


def process_xml(xml_str):
    logger = logging.getLogger(__name__)

    try:
        message = libspg.Message.from_string(xml_str)

        if isinstance(message, (libspg.bdo.SVCreateDownload,
                                libspg.bdo.SVDeleteDownload)):
            Message(
                direction='BDRtoBDO',
                status='received',
                service_prov_id=message.service_prov_id,
                invoke_id=message.invoke_id,
                message_date_time=message.message_date_time.replace(
                    tzinfo=utc),
                command_tag=type(message).__name__,
                xml=xml_str,
            ).save()

        else:
            logger.info('Ignoring message type: {0}'.format(
                type(message).__name__))

    except Exception as e:
        logger.exception(e)


class Command(BaseCommand):
    help = 'Import XML log from MACP SPG'

    def handle(self, *args, **options):

        # Process log files
        for path in args:

            # Initialize XML string
            xml_str = ''

            # Do not ignore the following message
            ignore = False

            # Read log file
            with open(path, 'r') as src:
                for line in src:

                    # New received message
                    if line.startswith('<<<'):

                        # Do not ignore the following message
                        ignore = False

                        # Process previous XML string if defined
                        if xml_str:
                            process_xml(xml_str)

                        # Start a new XML string
                        xml_str = line.split(' ', 1)[1].strip()

                    # New sent message
                    elif line.startswith('>>>'):

                        # Ignore the following message
                        ignore = True

                        # Process previous XML string if defined
                        if xml_str:
                            process_xml(xml_str)

                        xml_str = None

                    # Message continuation
                    else:
                        if not ignore:
                            # Append to the current string
                            xml_str += line.strip()

                # Finished processing the file
                else:
                    # Process the last XML string
                    process_xml(xml_str)
