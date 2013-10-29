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
    command = models.TextField()
    original = models.TextField()

    class Meta:
        ordering = ['message_date_time']

    def __unicode__(self):
        return '[{message_date_time} - {content_tag}] {command_tag}'.format(
            **self.__dict__)

    @staticmethod
    def from_string(xml_str):
        """Create an instance from a string"""

        from lxml import etree
        from bdo.main.schema import XMLParser

        # Parse the XML string and validate the document
        try:
            xml_tree = etree.fromstring(xml_str, parser=XMLParser)
        except Exception as e:
            raise Exception('Error processing XML:\n{0}\n{1}\n'.format(
                xml_str, e))

        # Unpack XML message elements
        [
            # Header
            [
                service_prov_id,
                invoke_id,
                message_date_time,
            ],

            # Content
            [content],

        ] = xml_tree

        # Get command element
        [command] = content

        # Return a new Message instance
        return Message(
            service_prov_id=service_prov_id.text,
            invoke_id=invoke_id.text,
            message_date_time=message_date_time.text,
            content_tag=content.tag.split('{urn:brazil:lnp:1.0}', 1)[1],
            command_tag=command.tag.split('{urn:brazil:lnp:1.0}', 1)[1],
            command=etree.tostring(command,
                                   encoding='UTF-8',
                                   standalone=False),
            original=xml_str,
        )

    def reply(self):
        """C"""

        if self.command_tag == 'SVCreateDownload':
            pass
        elif self.command_tag == 'SVDeleteDownload':
            pass
        elif self.command_tag == 'QueryBdoSVs':
            pass

    def to_string(self):
        """Generate XML string from instance"""

        from lxml import etree

        # Namespace mapping
        nsmap = {
            None: 'urn:brazil:lnp:1.0',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        }

        # Root
        xml = etree.Element('BDOMessage', nsmap=nsmap)

        # Header
        xml_header = etree.SubElement(xml, 'messageHeader')

        # Service provider ID
        xml_spid = etree.SubElement(xml_header, 'service_prov_id')
        xml_spid.text = str(self.service_prov_id)

        # Invoke ID
        xml_invoke = etree.SubElement(xml_header, 'invoke_id')
        xml_invoke.text = str(self.invoke_id)

        # Date/Time
        xml_datetime = etree.SubElement(xml_header, 'message_date_time')
        xml_datetime.text = self.message_date_time.strftime(
            '%Y-%m-%dT%H:%M:%SZ')

        # Content
        xml_content = etree.SubElement(xml, 'messageContent')

        # Content tag
        xml_content_tag = etree.SubElement(xml_content, str(self.content_tag))

        # Command
        xml_content_tag.append(etree.fromstring(str(self.command)))

        return etree.tostring(
            xml,
            encoding='UTF-8',
            pretty_print=True,
            standalone=False,
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
