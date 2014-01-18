import libspg
import libspg.bdo
import logging

from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from spyne.server.django import DjangoApplication
from spyne.model.primitive import Integer, Unicode
from spyne.service import ServiceBase
from spyne.protocol.soap import Soap11
from spyne.application import Application
from spyne.decorator import srpc

from bdosoa.main.models import Message, SubscriptionVersion


logger = logging.getLogger('django.main.views')


def process_message(xml_str):
    """Process BDR messages"""

    message = libspg.Message.from_string(xml_str)

    Message(
        service_prov_id=message.message_header.service_prov_id,
        invoke_id=message.message_header.invoke_id,
        message_date_time=message.message_header.message_date_time.replace(
            tzinfo=timezone.utc),
        command_tag=type(message).__name__,
        xml=xml_str
    ).save()

    if isinstance(message, libspg.bdo.SVCreateDownload):
        tn_version_id = message.message_content.subscription_tn_version_id
        data = message.message_content.subscription_data

        params = {
            'subscription_version_tn':
                tn_version_id.tn,
            'subscription_recipient_sp':
                data.subscription_recipient_sp,
            'subscription_recipient_eot':
                data.subscription_recipient_eot,
            'subscription_activation_timestamp':
                data.subscription_activation_timestamp.replace(
                    tzinfo=timezone.utc),
            'subscription_rn1':
                data.subscription_rn1,
            'subscription_new_cnl':
                data.subscription_new_cnl,
            'subscription_lnp_type':
                data.subscription_lnp_type,
            'subscription_download_reason':
                data.subscription_download_reason,
            'subscription_line_type':
                data.subscription_line_type,
            'subscription_optional_data':
                data.subscription_optional_data,
        }

        if data.broadcast_window_start_timestamp:
            params['subscription_broadcast_timestamp'] = \
                data.broadcast_window_start_timestamp.replace(
                    tzinfo=timezone.utc)

        try:
            try:
                sv = SubscriptionVersion.objects.get(
                    subscription_version_id=tn_version_id.version_id)

                for key, value in params:
                    setattr(sv, key, value)

                sv.save()

            except Exception:
                SubscriptionVersion(
                    subscription_version_id=tn_version_id.version_id,
                    **params
                ).save()

        except Exception as e:
            logger.error(str(e))
            reply = message.reply(status=False, error_info=str(e))

        else:
            reply = message.reply()

    elif isinstance(message, libspg.bdo.SVDeleteDownload):
        version_id = message.message_content.subscription_version_id
        data = message.message_content.subscription_delete_data

        try:
            SubscriptionVersion.objects.filter(
                subscription_version_id=version_id
            ).update(
                subscription_download_reason=data.subscription_download_reason,
                subscription_deletion_timestamp=timezone.now()
            )

        except Exception as e:
            logger.error(str(e))
            reply = message.reply(status=False, error_info=str(e))

        else:
            reply = message.reply()

    elif isinstance(message, libspg.bdo.QueryBdoSVs):
        query = message.message_content.query_expression
        query = query.lstrip('"').rstrip('"')

        reply = []
        sv_list = []

        if query:
            sv_list = SubscriptionVersion.objects.extra(where=[query]).exclude(
                subscription_deletion_timestamp__isnull=False)

        for sv in sv_list:
            sv_obj = libspg.SubscriptionVersionData(
                libspg.TNVersionId(
                    tn=sv.subscription_version_tn,
                    version_id=sv.subscription_version_id
                ),
                libspg.SubscriptionData(
                    subscription_recipient_sp=
                        sv.subscription_recipient_sp,
                    subscription_recipient_eot=
                        sv.subscription_recipient_eot,
                    subscription_activation_timestamp=
                        sv.subscription_activation_timestamp,
                    broadcast_window_start_timestamp=
                        sv.subscription_broadcast_timestamp,
                    subscription_rn1=
                        sv.subscription_rn1,
                    subscription_new_cnl=
                        sv.subscription_new_cnl,
                    subscription_lnp_type=
                        sv.subscription_lnp_type,
                    subscription_download_reason=
                        sv.subscription_download_reason,
                    subscription_line_type=
                        sv.subscription_line_type,
                    subscription_optional_data=
                        sv.subscription_optional_data
                )
            )

            reply.append(sv_obj)

        reply = message.reply(reply)

    else:
        raise TypeError('Invalid message type: {0}'.format(
            type(message).__name__))

    send_reply(str(reply))


def send_reply(xml_str):
    """Send SOAP reply"""
    pass


class SOAPService(ServiceBase):
    @srpc(Unicode, Unicode, _returns=Integer)
    def processRequest(header, message):
        try:
            process_message(message)

        except Exception as e:
            logger.error(e)
            return -1

        else:
            return 0


def index(request):
    return redirect('/admin/')


soap_app = csrf_exempt(
    DjangoApplication(
        Application(
            services=[SOAPService],
            tns='processResponse',
            in_protocol=Soap11(validator='lxml'),
            out_protocol=Soap11(),
        )
    )
)
