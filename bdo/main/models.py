from django.db import models


class Message(models.Model):
    """Mensagens enviadas e recebidas"""

    service_prov_id = models.CharField(max_length=4)
    invoke_id = models.IntegerField()
    message_date_time = models.DateTimeField()
    content_tag = models.CharField(max_length=8, choices=[
        ('BDOtoBDR', 'BDR<-BDO'),
        ('BDRtoBDO', 'BDR->BDO'),
        ('SOAtoBDR', 'BDR<-SOA'),
        ('BDRtoSOA', 'BDR->SOA'),
    ])
    command_tag = models.CharField(max_length=255)
    xml = models.TextField()
    processed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-message_date_time']

    def __unicode__(self):
        return '[{message_date_time} - {content_tag}] {command_tag}'.format(
            **self.__dict__)

    @staticmethod
    def from_string(xml_str):
        """Create instance from XML string"""

        from bdo.main import xml

        xml_obj = xml.from_string(xml_str)

        # Message content
        [content] = xml_obj.messageContent.getchildren()
        [command] = content.getchildren()

        return Message(
            service_prov_id=xml_obj.messageHeader.service_prov_id.text,
            invoke_id=xml_obj.messageHeader.invoke_id.text,
            message_date_time=xml_obj.messageHeader.message_date_time.text,
            content_tag=content.tag.split(xml.LNP_NS, 1)[1],
            command_tag=command.tag.split(xml.LNP_NS, 1)[1],
            xml=xml_str,
        )


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
            return '[+]{subscription_version_tn}'.format(**self.__dict__)
        else:
            return '[-]{subscription_version_tn}'.format(**self.__dict__)

    @staticmethod
    def from_string(xml_str):
        pass
