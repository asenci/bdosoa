import libspg
import libspg.bdo
import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt

from bdosoa.main.models import Message, ServiceProvider, SubscriptionVersion
from bdosoa.main.soap import SOAPApplication, SOAPClient


#
# Public views
#

def index(request):
    return redirect('/admin/')


@csrf_exempt
def soap(request, token=''):
    logger = logging.getLogger('{0}.soap'.format(__name__))

    if request.method != 'POST':
        raise Http404

    try:
        service_provider = ServiceProvider.objects.get(
            auth_token=token, enabled=True)
    except ServiceProvider.DoesNotExist:
        raise PermissionDenied

    logger.debug('New SOAP request for SPID: {0}\n{1}'.format(
        service_provider.service_prov_id, request))

    return soap_application(request, spid=service_provider.service_prov_id)


#
# SOAP processing routines
#

def receive_message(header, message, spid):
    logger = logging.getLogger('{0}.receive_message'.format(__name__))

    try:
        logger.debug('Receiving message for SPID: {0}'.format(spid))
        msg_obj = libspg.Message.from_string(message)

        if msg_obj.service_prov_id != spid:
            logger.error('Message SPID does not match token: {0}'.format(spid))
            raise PermissionDenied

        if not isinstance(msg_obj, libspg.bdo.BDRtoBDO):
            raise TypeError('Invalid message type: {0}'.format(
                type(msg_obj).__name__))

        msg_log = Message(
            direction='BDRtoBDO',
            status='received',
            service_prov_id=msg_obj.service_prov_id,
            invoke_id=msg_obj.invoke_id,
            message_date_time=msg_obj.message_date_time.replace(tzinfo=utc),
            command_tag=type(msg_obj).__name__,
            xml=message,
        )
        msg_log.save()

    except Exception as e:
        if e == PermissionDenied:
            raise e

        logger.exception(e)
        return '-1'

    logger.debug('Message enqueued: {0}'.format(msg_log))
    return '0'


def send_message(message):
    logger = logging.getLogger('{0}.send_message'.format(__name__))

    logger.debug('Processing: {0}'.format(message))

    service_provider = ServiceProvider.objects.get(
        service_prov_id=message.service_prov_id)

    soap_client = SOAPClient(
        service_provider.spg_soap_url, 'SPG/SoapServer')

    header = '{0}|{1}|{2:%s}'.format(
        message.service_prov_id,
        message.invoke_id,
        message.message_date_time,
    )

    try:
        result = soap_client.processRequest(header=header, message=message.xml)

    except Exception as e:
        logger.error(e)
        message.status = 'error'
        message.error = str(e)

    else:
        if result[0] == '0':
            message.status = 'sent'
        else:
            logger.error('Received "{0}" from: {1}'.format(
                result, service_provider.spg_soap_url))
            message.error = 'Received "{0}" reply from SPG'.format(result)

    message.save()
    logger.debug('Finished processing: {0}'.format(message))


soap_application = SOAPApplication('BDO/SoapServer')
soap_application.register_method('processRequest', receive_message)
soap_application.register_method('processResponse', receive_message)


#
# Messages processing routines
#

def process_message(message):
    logger = logging.getLogger('{0}.process_message'.format(__name__))

    try:
        logger.debug('Processing message: {0}'.format(message))

        if message.status == 'queued':
            send_message(message)

        elif message.status == 'received':
            try:
                msg_obj = libspg.Message.from_string(message.xml)

                if isinstance(msg_obj, libspg.bdo.SVCreateDownload):
                    reply = process_sv_create_download(msg_obj)
                elif isinstance(msg_obj, libspg.bdo.SVDeleteDownload):
                    reply = process_sv_delete_download(msg_obj)
                elif isinstance(msg_obj, libspg.bdo.QueryBdoSVs):
                    reply = process_query_bdo_svs(msg_obj)
                elif isinstance(msg_obj, libspg.bdo.SVQueryReply):
                    reply = None
                elif isinstance(msg_obj, libspg.bdo.BDRError):
                    reply = None
                else:
                    raise TypeError('Invalid message type: {0}'.format(
                        type(msg_obj).__name__))

                # Enqueue reply
                if reply is not None:
                    reply_log = Message(
                        direction='BDOtoBDR',
                        status='queued',
                        service_prov_id=reply.service_prov_id,
                        invoke_id=reply.invoke_id,
                        message_date_time=reply.message_date_time.replace(
                            tzinfo=utc),
                        command_tag=type(reply).__name__,
                        xml=str(reply)
                    )
                    reply_log.save()

                    logger.debug(
                        'Enqueued message reply: {0}'.format(reply_log))

            except Exception as e:
                logger.exception(e)
                message.status = 'error'
                message.error = str(e)

            else:
                message.status = 'processed'

            message.save()

    except Exception as e:
        logger.exception(e)
        message.error = str(e)
        message.save()

    else:
        logger.debug('Finished processing message: {0}'.format(message))


def process_sv_create_download(msg_obj):
    logger = logging.getLogger(
        '{0}.process_sv_create_download'.format(__name__))

    tn_version_id = msg_obj.message_content.subscription_tn_version_id
    data = msg_obj.message_content.subscription_data

    params = {
        'subscription_version_tn':
            tn_version_id.tn,
        'subscription_recipient_sp':
            data.subscription_recipient_sp,
        'subscription_recipient_eot':
            data.subscription_recipient_eot,
        'subscription_activation_timestamp':
            data.subscription_activation_timestamp.replace(tzinfo=utc),
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
            data.broadcast_window_start_timestamp.replace(tzinfo=utc)

    try:
        try:
            sv = SubscriptionVersion.objects.get(
                service_prov_id=msg_obj.service_prov_id,
                subscription_version_id=tn_version_id.version_id)

            for key, value in params.items():
                setattr(sv, key, value)

            sv.save()

        except SubscriptionVersion.DoesNotExist:
            SubscriptionVersion(
                service_prov_id=msg_obj.service_prov_id,
                subscription_version_id=tn_version_id.version_id,
                **params).save()

    except Exception as e:
        logger.exception(e)
        return msg_obj.reply(status=False, error_info=str(e))

    else:
        return msg_obj.reply()


def process_sv_delete_download(msg_obj):
    logger = logging.getLogger(
        '{0}.process_sv_delete_download'.format(__name__))

    version_id = msg_obj.message_content.subscription_version_id
    data = msg_obj.message_content.subscription_delete_data

    try:
        SubscriptionVersion.objects.filter(
            service_prov_id=msg_obj.service_prov_id,
            subscription_version_id=version_id,
        ).update(
            subscription_download_reason=data.subscription_download_reason,
            subscription_deletion_timestamp=
                msg_obj.message_date_time.replace(tzinfo=utc),
        )

    except Exception as e:
        logger.exception(e)
        return msg_obj.reply(status=False, error_info=str(e))

    else:
        return msg_obj.reply()


def process_query_bdo_svs(msg_obj):
    logger = logging.getLogger('{0}.process_query_bdo_svs'.format(__name__))

    if isinstance(msg_obj, libspg.bdo.QueryBdoSVs):
        try:
            query = msg_obj.message_content.query_expression
            query = query.lstrip('"').rstrip('"')

            reply_list = []
            sv_list = []

            if query:
                sv_list = SubscriptionVersion.objects.filter(
                    service_prov_id=msg_obj.service_prov_id,
                    subscription_deletion_timestamp__isnull=True,
                ).extra(where=[query])

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
                        sv.subscription_optional_data,
                    )
                )

                reply_list.append(sv_obj)

            return msg_obj.reply(reply_list)

        except Exception as e:
            logger.exception(e)
            raise e