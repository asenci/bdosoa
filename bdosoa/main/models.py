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

    message_date_time = models.DateTimeField()
    service_prov_id = models.CharField(max_length=4)
    invoke_id = models.IntegerField()
    direction = models.CharField(max_length=8, choices=[
        ('BDOtoBDR', 'BDR<-BDO'),
        ('BDRtoBDO', 'BDR->BDO'),
        ('SOAtoBDR', 'BDR<-SOA'),
        ('BDRtoSOA', 'BDR->SOA')])
    command_tag = models.CharField(max_length=255)
    status = models.CharField(max_length=9, choices=[
        ('error', 'Error'),
        ('received', 'Received'),
        ('processed', 'Processed'),
        ('queued', 'Queued'),
        ('sent', 'Sent')])
    message_body = models.TextField()
    error_info = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-message_date_time']

    def __unicode__(self):
        return '[{message_date_time}|{service_prov_id}|{invoke_id}]' \
               ' {command_tag}'.format(**self.__dict__)


class QueuedMessage(models.Model):
    """Fila de mensagens"""

    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.OneToOneField('Message')

    message_date_time = property(lambda self: self.message.message_date_time)
    service_prov_id = property(lambda self: self.message.service_prov_id)
    invoke_id = property(lambda self: self.message.invoke_id)
    direction = property(lambda self: self.message.direction)
    command_tag = property(lambda self: self.message.command_tag)
    status = property(lambda self: self.message.status)
    message_body = property(lambda self: self.message.message_body)
    error_info = property(lambda self: self.message.error_info)

    class Meta:
        ordering = ['timestamp']

    def __unicode__(self):
        return '{0} - [{service_prov_id}|{invoke_id}] {command_tag}'.format(
            self.id, **self.message.__dict__)

    @classmethod
    def flush(cls):
        from bdosoa.main.messages import process_message

        for item in cls.objects.all():
            process_message(item.message)



class ServiceProvider(models.Model):
    """Provedor de Servico"""

    service_prov_id = models.CharField(max_length=4, unique=True)
    auth_token = models.CharField(max_length=32, unique=True,
                                  default=gen_token)
    spg_soap_url = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)

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

from django.db.models.signals import post_save
from django.dispatch import receiver

# noinspection PyUnusedLocal
@receiver(post_save, sender=Message, dispatch_uid='message_post_save')
def message_post_save(sender, **kwargs):
    print 'message_post_save'
    instance = kwargs.get('instance')
    print instance

    if instance.status in ['received', 'queued']:
        print QueuedMessage.objects.create(message=instance)
    else:
        print 'deleted'
        QueuedMessage.objects.get(message=instance).delete()

try:
    import uwsgi

except ImportError:
    # Synchronous processing

    # noinspection PyUnusedLocal
    @receiver(post_save, sender=QueuedMessage, dispatch_uid='queue_post_save')
    def queue_post_save(sender, **kwargs):
        QueuedMessage.flush()

else:
    # Asynchronous processing

    # noinspection PyUnusedLocal
    @receiver(post_save, sender=QueuedMessage, dispatch_uid='queue_post_save')
    def queue_post_save(sender, **kwargs):
        print 'queue_post_save'
        uwsgi.mule_msg('flush_queue')
