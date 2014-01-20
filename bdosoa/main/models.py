from django.db import models


def gen_token(size=32):
    """Gerenate random tokens"""
    import string
    from random import SystemRandom

    charlist = string.letters + string.digits

    passwd = [SystemRandom().choice(charlist) for i in range(size)]

    return string.join(passwd, sep='')


class Message(models.Model):
    """Mensagens enviadas e recebidas"""

    direction = models.CharField(max_length=8, choices=[
        ('BDOtoBDR', 'BDR<-BDO'),
        ('BDRtoBDO', 'BDR->BDO'),
        ('SOAtoBDR', 'BDR<-SOA'),
        ('BDRtoSOA', 'BDR->SOA')])
    status = models.CharField(max_length=9, choices=[
        ('error', 'Error'),
        ('processed', 'Processed'),
        ('queued', 'Queued'),
        ('received', 'Received'),
        ('sent', 'Sent')])
    service_prov_id = models.CharField(max_length=4)
    invoke_id = models.IntegerField()
    message_date_time = models.DateTimeField()
    command_tag = models.CharField(max_length=255)
    xml = models.TextField()
    error = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-message_date_time']

    def __unicode__(self):
        return '[{message_date_time}|{service_prov_id}|{invoke_id}] ' \
               '{command_tag}'.format(**self.__dict__)


class ServiceProvider(models.Model):
    """Provedor de Servico"""

    service_prov_id = models.CharField(max_length=4, db_index=True)
    auth_token = models.CharField(max_length=32, db_index=True, unique=True,
                                  default=gen_token)
    spg_soap_url = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ['service_prov_id']

    def __unicode__(self):
        return '{service_prov_id}'.format(**self.__dict__)


class SubscriptionVersion(models.Model):
    """Versao de Subscricao (Bilhete de portabilidade)"""

    service_prov_id = models.CharField(max_length=4)
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

from bdosoa.main.views import process_message


@receiver(post_save, sender=Message, dispatch_uid='message_post_save')
def message_post_save(sender, **kwargs):
    message = kwargs.get('instance')

    if message.status in ['received', 'queued']:
        process_message(message)

