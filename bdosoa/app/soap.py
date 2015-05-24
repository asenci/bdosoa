"""
bdosoa - SOAP requests processing
"""

import cherrypy
import libspg
import sys

from datetime import datetime
from email.mime.text import MIMEText
from libspg.bdo import (BDRError, BDRtoBDO, BDOtoBDR, QueryBdoSVs,
                        SVCreateDownload, SVDeleteDownload, SVQueryReply)
from traceback import format_exception
from subprocess import Popen, PIPE

from bdosoa.lib.soap import SOAPApplication, SOAPClient
from bdosoa.model import ServiceProvider, SubscriptionVersion, SyncTask
from bdosoa.model.meta import NoResultFound


class SOAP(object):
    """Process SOAP requests"""

    def __init__(self):
        self.__msg_handlers__ = {
            BDRError: lambda x: None,
            QueryBdoSVs: self.process_query_bdo_svs,
            SVCreateDownload: self.process_sv_create_download,
            SVDeleteDownload: self.process_sv_delete_download,
            SVQueryReply: lambda x: None,
        }

        self.soap_app = SOAPApplication(namespace='SPG/SoapServer')
        self.soap_app.register_method('processResponse', self.receive_soap)

    @staticmethod
    def logger(msg="", msg_obj=None, context='', severity=20, traceback=False):
        """Log messages

        :param str msg: Message
        :param libspg.Message msg_obj: Message object
        :param str context: Message context
        :param int severity: Severity level
        :param bool traceback: Include exception traceback if true
        """

        if msg_obj:
            try:
                context = '[{0}|{1}|{2}]'.format(
                    msg_obj.service_prov_id, msg_obj.invoke_id,
                    msg_obj.__class__.__name__)

            except:
                cherrypy.log.error('Error formatting log message. ', 'ENGINE',
                                   severity=40, traceback=True)

        cherrypy.log.error(msg=msg, context=context, severity=severity,
                           traceback=traceback)

    @cherrypy.expose
    def index(self, spid=None, token=None):
        """Receive SOAP envelope

        :param str spid: Service provider ID
        :param str token: Access token
        :return: A SOAP response
        :rtype: str
        """

        if cherrypy.request.method != 'POST':
            cherrypy.response.headers['Allow'] = 'POST'
            raise cherrypy.HTTPError(405)

        # Check access credentials
        try:
            cherrypy.request.service_provider = \
                cherrypy.request.db.query(ServiceProvider).filter_by(
                    spid=spid, token=token, enabled=True).one()

        except NoResultFound:
            raise cherrypy.HTTPError(403)

        # Process request
        status_code, response = self.soap_app.process_request(
            cherrypy.request.body.read())

        # Return response
        cherrypy.response.status = status_code
        return response

    # noinspection PyPep8Naming,PyUnusedLocal
    def receive_soap(self, header, xmlMessage):
        """Receive SOAP request and enqueue message for processing

        :param str header: Message header
        :param str xmlMessage: Message
        :return: "0" if no errors occurred else "-1"
        :rtype: str
        """

        sp = cherrypy.request.service_provider
        msg_obj = libspg.Message.from_string(xmlMessage)

        # Check the service provider id on the SPG message
        if msg_obj.service_prov_id != sp.spid:
            raise ValueError(
                'Message SPID ({0}) does not match request SPID ({1})'
                .format(msg_obj.service_prov_id, sp.spid))

        # Check SPG message type
        if not isinstance(msg_obj, BDRtoBDO):
            raise TypeError('Invalid message: {0!r}'.format(msg_obj))

        # Process SPG message
        try:
            self.process_message(msg_obj)

        # Log and mail the exception if the processing fails
        except:
            self.logger('Error processing message. ', msg_obj, severity=40,
                        traceback=True)

            mail = MIMEText(''.join(format_exception(*sys.exc_info())))
            mail['To'] = 'root'
            mail['Subject'] = \
                'BDOSOA - Error processing message {0} for SPID {1}' \
                .format(msg_obj.invoke_id, msg_obj.service_prov_id)

            p = Popen(['/usr/sbin/sendmail', '-t'], stdin=PIPE)
            p.communicate(mail.as_string())
            p.stdin.close()
            p.wait()

            return '-1'

        return '0'

    def process_message(self, msg_obj):
        """Process SPG messages

        :param libspg.Message msg_obj: Message object
        """

        # Inbound messages
        if isinstance(msg_obj, BDRtoBDO):
            self.input(msg_obj)

        # Outbound messages
        elif isinstance(msg_obj, BDOtoBDR):
            self.output(msg_obj)

        else:
            raise NotImplementedError('No handler for: {0!r}'.format(msg_obj))

    def input(self, msg_obj):
        """Process inbound messages

        :param libspg.Message msg_obj: Message object
        """

        self.logger('Received message.', msg_obj)

        # Get message handler
        handler = self.__msg_handlers__.get(type(msg_obj))

        if handler is None:
            raise NotImplementedError('No handler for message: {0!r}'
                                      .format(msg_obj))

        self.logger('Handler: {0!r}'.format(handler), msg_obj,
                    severity=10)

        # Process message
        reply = handler(msg_obj)

        # Send reply
        if reply is not None:
            self.logger('Handler generated reply: {0!r}'
                        .format(reply), msg_obj, severity=10)

            self.process_message(reply)

        self.logger('Finished processing message.', msg_obj, severity=10)

    def output(self, msg_obj):
        """Output handling thread

        :param libspg.Message msg_obj: Message object
        """

        self.logger('Sending message.', msg_obj)

        # Get the message service provider
        sp = cherrypy.request.db.query(ServiceProvider).filter_by(
            spid=msg_obj.service_prov_id, enabled=True).one()

        self.logger('Sending message to: {0}'
                    .format(sp.spg_url), msg_obj, severity=10)

        soap_client = SOAPClient(sp.spg_url, 'SPG/SoapServer')

        header = '{0}|{1}|{2:%s}'.format(
            msg_obj.service_prov_id,
            msg_obj.invoke_id,
            msg_obj.message_date_time,
        )

        # Send the message to the service provider SPG
        response = soap_client.processRequest(
            header=header, message=str(msg_obj))

        # Check the SPG response
        if response != ('0',):
            raise ValueError('Received "{0}" from SPG'.format(response))

        self.logger('Finished processing message.', msg_obj, severity=10)

    def process_sv_create_download(self, msg_obj):
        """Create new subscription version

        :param SVCreateDownload msg_obj: SVCreateDownload message
        """
        sp = cherrypy.request.service_provider
        tn_version_id = msg_obj.message_content.subscription_tn_version_id
        data = msg_obj.message_content.subscription_data

        # Get the subscription version
        try:
            sv = cherrypy.request.db.query(SubscriptionVersion).filter_by(
                spid=msg_obj.service_prov_id,
                subscription_version_id=tn_version_id.version_id
            ).one()

            self.logger('Updating subscription version: {0}'.format(
                tn_version_id.version_id), msg_obj)

        # Create a new subscription version if it does not already exist
        except NoResultFound:
            sv = SubscriptionVersion(
                spid=msg_obj.service_prov_id,
                subscription_version_id=tn_version_id.version_id)
            cherrypy.request.db.add(sv)
            cherrypy.request.db.flush()

            self.logger('New subscription version: {0}'.format(
                tn_version_id.version_id), msg_obj)

        # Update the subscription version attributes
        sv.subscription_version_tn = tn_version_id.tn
        sv.subscription_recipient_sp = data.subscription_recipient_sp
        sv.subscription_recipient_eot = data.subscription_recipient_eot
        sv.subscription_activation_timestamp = \
            data.subscription_activation_timestamp
        sv.subscription_broadcast_timestamp = \
            data.broadcast_window_start_timestamp or None
        sv.subscription_rn1 = data.subscription_rn1
        sv.subscription_new_cnl = data.subscription_new_cnl
        sv.subscription_lnp_type = data.subscription_lnp_type
        sv.subscription_line_type = data.subscription_line_type
        sv.subscription_optional_data = data.subscription_optional_data

        # Do not change the download reason on deleted subscription versions
        # This allows for a create or modify message to be processed after a
        # delete message keeping the subscription version state
        if sv.subscription_deletion_timestamp is None:
            sv.subscription_download_reason = data.subscription_download_reason

        # Create the sync tasks
        for client in sp.sync_clients.filter_by(enabled=True):
            task = SyncTask(syncclient_id=client.id,
                            subscriptionversion_id=sv.id)
            cherrypy.request.db.add(task)
            cherrypy.request.db.flush()

            self.logger('Added sync task: {0}'.format(task.id), msg_obj)

        return msg_obj.reply()

    def process_sv_delete_download(self, msg_obj):
        """Remove a subscription version

        :param SVDeleteDownload msg_obj: SVDeleteDownload message
        """

        sp = cherrypy.request.service_provider
        version_id = msg_obj.message_content.subscription_version_id
        data = msg_obj.message_content.subscription_delete_data

        # Get the subscription version
        try:
            sv = cherrypy.request.db.query(SubscriptionVersion).filter_by(
                spid=msg_obj.service_prov_id,
                subscription_version_id=version_id,
            ).one()

        # Subscription version not found, no processing needed
        except NoResultFound:
            self.logger('Subscription version not found: {0}'
                        .format(version_id), msg_obj)

        else:
            # Update the subscription version attributes
            sv.subscription_download_reason = data.subscription_download_reason
            sv.subscription_deletion_timestamp = \
                data.broadcast_window_start_timestamp or \
                datetime.utcnow()

            self.logger('Removed subscription version: {0}'
                        .format(version_id), msg_obj)

            # Create the sync tasks
            for client in sp.sync_clients.filter_by(enabled=True):
                task = SyncTask(syncclient_id=client.id,
                                subscriptionversion_id=sv.id)
                cherrypy.request.db.add(task)
                cherrypy.request.db.flush()

                self.logger('Added sync task: {0}'.format(task.id), msg_obj)

        return msg_obj.reply()

    def process_query_bdo_svs(self, msg_obj):
        """Query subscription versions

        :param QueryBdoSVs msg_obj: QueryBdoSVs message
        """

        spid = msg_obj.service_prov_id
        query_string = msg_obj.message_content.query_expression

        self.logger('Query string: {0}'.format(query_string), msg_obj)

        if query_string.startswith('"') and query_string.endswith('"'):
            query_string = query_string.lstrip('" ').rstrip(' "')

        if not query_string:
            raise ValueError('A query expression must be specified')

        # Get the subscription versions
        svs = cherrypy.request.db.query(SubscriptionVersion).filter_by(
            spid=spid, subscription_deletion_timestamp=None,
        ).filter(query_string).all()

        # Build the query response
        query_result = [
            libspg.SubscriptionVersionData(
                libspg.TNVersionId(
                    tn=sv.subscription_version_tn,
                    version_id=sv.subscription_version_id,
                ),
                libspg.SubscriptionData(
                    subscription_recipient_sp=sv.subscription_recipient_sp,
                    subscription_recipient_eot=sv.subscription_recipient_eot,
                    subscription_activation_timestamp=sv.subscription_activation_timestamp,
                    broadcast_window_start_timestamp=sv.subscription_broadcast_timestamp,
                    subscription_rn1=sv.subscription_rn1,
                    subscription_new_cnl=sv.subscription_new_cnl,
                    subscription_lnp_type=sv.subscription_lnp_type,
                    subscription_download_reason=sv.subscription_download_reason,
                    subscription_line_type=sv.subscription_line_type,
                    subscription_optional_data=sv.subscription_optional_data,
                )
            )

            for sv in svs
        ]

        self.logger('Query result: {0}'
                    .format([sv.subscription_tn_version_id.version_id
                             for sv in query_result]), msg_obj)

        # Send the query result
        return msg_obj.reply(query_result)
