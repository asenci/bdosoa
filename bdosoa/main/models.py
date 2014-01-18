from django.db import models


class Message(models.Model):
    """Mensagens enviadas e recebidas"""

    service_prov_id = models.CharField(max_length=4)
    invoke_id = models.IntegerField()
    message_date_time = models.DateTimeField()
    command_tag = models.CharField(max_length=255)
    xml = models.TextField()

    class Meta:
        ordering = ['-message_date_time']

    def __unicode__(self):
        return '[{message_date_time}|{service_prov_id}|{invoke_id}] ' \
               '{command_tag}'.format(**self.__dict__)


class SubscriptionVersion(models.Model):
    """Versao de Subscricao (Bilhete de portabilidade)"""

    subscription_version_id = models.IntegerField(primary_key=True)
    subscription_version_tn = models.CharField(max_length=11, db_index=True)
    subscription_recipient_sp = models.CharField(max_length=4)
    subscription_recipient_eot = models.CharField(max_length=3)
    subscription_activation_timestamp = models.DateTimeField()
    subscription_broadcast_timestamp = models.DateTimeField(blank=True,
                                                            null=True)
    subscription_rn1 = models.CharField(max_length=5)
    subscription_new_cnl = models.CharField(max_length=5, blank=True,
                                            null=True)
    subscription_lnp_type = models.CharField(max_length=4, choices=[
        ('lspp', 'Inter-Operadora'),
        ('lisp', 'Intrinseca'),
    ])
    subscription_download_reason = models.CharField(max_length=8, choices=[
        ('new', 'Novo'),
        ('delete', 'Removido'),
        ('modified', 'Modificado'),
    ])
    subscription_line_type = models.CharField(max_length=5, choices=[
        ('Basic', 'Assinante'),
        ('DDR', 'Tronco DDR'),
        ('CNG', 'CNG'),
    ])
    subscription_optional_data = models.TextField(blank=True, null=True)
    subscription_deletion_timestamp = models.DateTimeField(blank=True,
                                                           null=True)

    class Meta:
        index_together = [
            ['subscription_version_tn', 'subscription_download_reason'],
            [
                'subscription_version_tn',
                'subscription_activation_timestamp',
                'subscription_deletion_timestamp'
            ],
        ]
        ordering = [
            'subscription_version_tn',
            'subscription_activation_timestamp',
        ]

    def __unicode__(self):
        return '[{subscription_version_id}] {subscription_version_tn}'.format(
            **self.__dict__)