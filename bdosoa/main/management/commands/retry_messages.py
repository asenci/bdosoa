import logging

from django.core.management.base import BaseCommand

from bdosoa.main.models import Message
from bdosoa.main.views import process_message


class Command(BaseCommand):
    help = 'Retry stalled messages'

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)

        try:
            logger.info('Retrying stalled messages')

            for message in Message.objects.filter(status='queued'):
                process_message(message)

            for message in Message.objects.filter(status='received'):
                process_message(message)

        except Exception as e:
            logger.exception(e)
