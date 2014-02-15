import logging
import libspg
import libspg.bdo

from django.core.management.base import BaseCommand
from django.db.models.signals import post_save
from django.utils.timezone import utc

from bdosoa.main.messages import MESSAGE_HANDLERS
from bdosoa.main.models import Message


class Command(BaseCommand):
    help = 'Import messages from log'

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        post_save.receivers = None

        try:

            # Process log files
            for path in args:

                # Read log file
                with open(path, 'r') as src:

                    for line in src:

                        message = libspg.Message.from_string(line)

                        msg_log = Message.objects.create(
                            message_date_time=
                                message.message_date_time.replace(tzinfo=utc),
                            service_prov_id=message.service_prov_id,
                            invoke_id=message.invoke_id,
                            direction='BDRtoBDO',
                            command_tag=type(message).__name__,
                            status='processed',
                            message_body=line,
                        )

                        try:
                            handler = MESSAGE_HANDLERS.get(type(message))
                            handler(message)

                        except Exception as e:
                            msg_log.error_info += str(e) + '\n\n'
                            msg_log.status = 'error'
                            msg_log.save()
                            logger.exception(e)

        except Exception as e:
            logger.exception(e)
