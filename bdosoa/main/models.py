from django.db import models


def gen_token(size=32):
    """Generate random tokens"""
    import string
    from random import SystemRandom

    charlist = string.letters + string.digits

    # noinspection PyUnusedLocal
    passwd = [SystemRandom().choice(charlist) for i in range(size)]

    return string.join(passwd, sep='')


class Message(models.Model):
    """Log de Mensagens"""

    message_date_time = models.DateTimeField(db_index=True)
    service_prov_id = models.CharField(max_length=4)
    invoke_id = models.BigIntegerField()
    direction = models.CharField(max_length=8, choices=[
        ('BDRtoBDO', 'BDR->BDO'),
        ('BDOtoBDR', 'BDR<-BDO'),
        ('BDRtoSOA', 'BDR->SOA'),
        ('SOAtoBDR', 'BDR<-SOA')])
    command_tag = models.CharField(max_length=255)
    status = models.CharField(max_length=6, choices=[
        ('queued', 'Queued'),
        ('error', 'Error'),
        ('done', 'Done')])
    message_body = models.TextField()
    error_info = models.TextField(blank=True, default='')

    class Meta:
        index_together = [
            ['direction', 'status'],
        ]

        ordering = ['-message_date_time']

    def __unicode__(self):
        return '[{message_date_time}|{service_prov_id}|{invoke_id}]' \
               ' {command_tag}'.format(**self.__dict__)


class ServiceProvider(models.Model):
    """Provedor de Servico"""

    service_prov_id = models.CharField(max_length=4, unique=True)
    enabled = models.BooleanField(default=True)
    auth_token = models.CharField(max_length=32, unique=True,
                                  default=gen_token)
    spg_soap_url = models.CharField(max_length=255)
    sync_api_url = models.CharField(max_length=255)

    class Meta:
        index_together = [
            ['auth_token', 'enabled'],
        ]

        ordering = ['service_prov_id']

    def __unicode__(self):
        return '[{service_prov_id}] {auth_token}'.format(**self.__dict__)


class SubscriptionVersion(models.Model):
    """Versao de Subscricao (Bilhete de portabilidade)"""

    service_prov_id = models.CharField(max_length=4, db_index=True)
    subscription_version_id = models.IntegerField(primary_key=True)
    subscription_version_tn = models.CharField(max_length=11, db_index=True)
    subscription_recipient_sp = models.CharField(max_length=4)
    subscription_recipient_eot = models.CharField(max_length=3)
    subscription_activation_timestamp = models.DateTimeField(db_index=True)
    subscription_broadcast_timestamp = \
        models.DateTimeField(blank=True, null=True)
    subscription_rn1 = models.CharField(max_length=5)
    subscription_new_cnl = \
        models.CharField(max_length=5, blank=True, null=True)
    subscription_lnp_type = models.CharField(max_length=4, choices=[
        ('lspp', 'Inter-Operadora'),
        ('lisp', 'Intrinseca')])
    subscription_download_reason = models.CharField(max_length=8, choices=[
        ('new', 'Novo'),
        ('delete', 'Removido'),
        ('modified', 'Modificado')])
    subscription_line_type = models.CharField(max_length=5, choices=[
        ('Basic', 'Assinante'),
        ('DDR', 'Tronco DDR'),
        ('CNG', 'CNG')])
    subscription_optional_data = models.TextField(blank=True, null=True)
    subscription_deletion_timestamp = \
        models.DateTimeField(blank=True, null=True, db_index=True)

    class Meta:
        index_together = [
            [
                'service_prov_id',
                'subscription_version_tn',
                'subscription_activation_timestamp',
                'subscription_deletion_timestamp'
            ],
        ]
        ordering = [
            'subscription_version_tn',
            'subscription_version_id',
        ]

    def __unicode__(self):
        return '[{subscription_version_id}] {subscription_version_tn}'.format(
            **self.__dict__)


#
# Signals handling
#

import logging
import threading

from django.db.models.signals import post_save
from django.dispatch import receiver

keep_flushing_in = threading.Event()
keep_flushing_out = threading.Event()

def flush_messages(direction):

    count = 0
    logger = logging.getLogger(
        '{0}.flush_messages_{1}'.format(__name__, direction))

    logger.debug('Flushing messages')

    t = threading.current_thread()
    t.keep_flushing.set()

    while t.keep_flushing.is_set():
        t.keep_flushing.clear()

        count += 1
        logger.debug('Iteration: {0}'.format(count))

        from bdosoa.main.messages import process_message

        msgs = Message.objects \
            .exclude(status='done') \
            .filter(direction=direction) \
            .order_by('message_date_time')

        for msg in msgs:
            try:
                process_message(msg)

            except Exception as e:
                logger.exception(e)
                break

    logger.debug('Finished flushing messages')


# noinspection PyUnusedLocal
@receiver(post_save, sender=Message, dispatch_uid='message_post_save')
def message_post_save(sender, **kwargs):
    instance = kwargs.get('instance')

    if instance.status == 'queued':

        for t in threading.enumerate():
            if t.name == instance.direction:
                t.keep_flushing.set()
                break

        else:
            t = threading.Thread(name=instance.direction,
                                 target=flush_messages,
                                 args=(instance.direction,))
            t.keep_flushing = threading.Event()
            t.daemon = True
            t.start()