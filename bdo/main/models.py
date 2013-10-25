from django.db import models


class SubscriptionVersion(models.Model):
    """Versao de Subscricao (Bilhete de portabilidade)"""

    subscription_version_id = models.IntegerField(primary_key=True)
    subscription_version_tn = models.CharField(max_length=11, db_index=True)
    subscription_recipient_sp = models.CharField(max_length=4)
    subscription_recipient_eot = models.CharField(max_length=3)
    subscription_activation_timestamp = models.DateTimeField()
    broadcast_window_start_timestamp = models.DateTimeField(blank=True,
                                                            null=True)
    subscription_rn1 = models.CharField(max_length=5)
    subscription_new_cnl = models.CharField(max_length=5)
    subscription_lnp_type = models.CharField(max_length=4, choices=[
        ('lspp', 'Intrinseca'),
        ('lisp', 'Inter-Operadora'),
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
    subscription_optional_data = models.TextField(blank=True)
    active = models.BooleanField(default=True, db_index=True)
    deletion_timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        index_together = [
            ['subscription_version_tn', 'active'],
            [
                'subscription_version_tn',
                'subscription_activation_timestamp',
                'deletion_timestamp'
            ],
        ]
        ordering = [
            'subscription_version_tn',
            'subscription_activation_timestamp',
        ]

        def __unicode__(self):
            if self.active:
                return '[+]{subscription_version_tn}'.format(**self)
            else:
                return '[-]{subscription_version_tn}'.format(**self)


class BDOMessage(models.Model):
    """Mensagens enviadas e recebidas"""

    outbound = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255)
    message = models.TextField()

    class Meta:
        ordering = ['timestamp']

    def __unicode__(self):
        if self.outbound:
            return '-> [{timestamp}] {description}'.format(**self)
        else:
            return '<- [{timestamp}] {description}'.format(**self)
