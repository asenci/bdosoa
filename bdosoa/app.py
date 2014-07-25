"""
bdosoa - exposed applications
"""

import cherrypy
import libspg
import libspg.bdo
import sys

from email.mime.text import MIMEText
from traceback import format_exception
from subprocess import Popen, PIPE

import bdosoa.model
import bdosoa.model.meta
import bdosoa.soap
import bdosoa.util


# Database access configuration
cherrypy.config.namespaces['database'] = \
    bdosoa.model.meta.Session.config_handler

# Logging configuration
cherrypy.config.namespaces['add_log'] = \
    lambda k, v: bdosoa.util.config_logging(v)


class Root(object):
    """Application Root"""

    @cherrypy.expose
    def index(self):
        """Index page"""

        return """<html>
          <head></head>
          <body>
            <form method="post" action="query/">
              Query: <input type="text" name="query_string" />
              <button type="submit">Consultar</button>
            </form>
          </body>
        </html>"""

    @cherrypy.expose
    def query(self, query_string):
        """Query BDO SVs

        :param str query_string: Query string
        :return: The query result
        :rtype: str
        """
        # todo: implement SV query

        if cherrypy.request.method != 'POST':
            cherrypy.response.headers['Allow'] = 'POST'
            raise cherrypy.HTTPError(405)

        return query_string


@cherrypy.popargs('spid', 'token')
class SOAP(object):
    """Process SOAP requests"""

    def __init__(self):
        self.__msg_handlers__ = {
            libspg.bdo.BDRError: lambda x: None,
            libspg.bdo.QueryBdoSVs: self.process_query_bdo_svs,
            libspg.bdo.SVCreateDownload: self.process_sv_create_download,
            libspg.bdo.SVDeleteDownload: self.process_sv_delete_download,
            libspg.bdo.SVQueryReply: lambda x: None,
        }

        self.soap_app = bdosoa.soap.SOAPApplication(namespace='SPG/SoapServer')
        self.soap_app.register_method('processResponse', self.receive_soap)

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

        try:
            cherrypy.request.service_provider = \
                bdosoa.model.ServiceProvider.get_by(
                    spid=spid, token=token, enabled=True)

        except bdosoa.model.ServiceProvider.NoResultFound:
            raise cherrypy.HTTPError(403)

        status_code, response = self.soap_app.process_request(
            cherrypy.request.body.read())

        cherrypy.response.status = status_code
        return response

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

    # noinspection PyPep8Naming,PyUnusedLocal
    def receive_soap(self, header, xmlMessage):
        """Receive SOAP request and enqueue message for processing

        :param str header: Message header
        :param str xmlMessage: Message
        :return: "0" if no errors occurred else "-1"
        :rtype: str
        """

        service_provider = cherrypy.request.service_provider

        msg_obj = libspg.Message.from_string(xmlMessage)

        if msg_obj.service_prov_id != service_provider.spid:
            raise ValueError(
                'Message SPID ({0}) does not match request SPID ({1})'
                .format(msg_obj.service_prov_id, service_provider.spid))

        if not isinstance(msg_obj, libspg.bdo.BDRtoBDO):
            raise TypeError('Invalid message: {0!r}'.format(msg_obj))

        try:
            self.process_message(msg_obj)

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
        """Process received messages and send reply

        :param libspg.Message msg_obj: Message object
        """

        if isinstance(msg_obj, libspg.bdo.BDRtoBDO):
            self.input(msg_obj)

        elif isinstance(msg_obj, libspg.bdo.BDOtoBDR):
            self.output(msg_obj)

        else:
            raise NotImplementedError('No handler for: {0!r}'.format(msg_obj))

    def input(self, msg_obj):
        """Process inbound messages

        :param libspg.Message msg_obj: Message object
        """

        self.logger('Received message.', msg_obj)

        handler = self.__msg_handlers__.get(type(msg_obj))

        if handler is None:
            raise NotImplementedError('No handler for message: {0!r}'
                                      .format(msg_obj))

        self.logger('Handler: {0!r}'.format(handler), msg_obj,
                    severity=10)

        reply = handler(msg_obj)

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

        service_provider = bdosoa.model.ServiceProvider.get_by(
            spid=msg_obj.service_prov_id, enabled=True)

        self.logger('Sending message to: {0}'
                    .format(service_provider.spg_url),
                    msg_obj, severity=10)

        soap_client = bdosoa.soap.SOAPClient(
            service_provider.spg_url, 'SPG/SoapServer')

        header = '{0}|{1}|{2:%s}'.format(
            msg_obj.service_prov_id,
            msg_obj.invoke_id,
            msg_obj.message_date_time,
        )

        result = soap_client.processRequest(
            header=header, message=str(msg_obj))

        if result != ('0',):
            raise ValueError('Received "{0}" from SPG'.format(result))

        self.logger('Finished processing message.', msg_obj, severity=10)

    def process_sv_create_download(self, msg_obj):
        """Create new subscription version

        :param SVCreateDownload msg_obj: SVCreateDownload message
        """

        tn_version_id = msg_obj.message_content.subscription_tn_version_id
        data = msg_obj.message_content.subscription_data

        try:
            sv = bdosoa.model.SubscriptionVersion.get_by(
                spid=msg_obj.service_prov_id,
                subscription_version_id=tn_version_id.version_id)

            self.logger('Updating subscription version: {0}'.format(
                tn_version_id.version_id), msg_obj)

        except bdosoa.model.SubscriptionVersion.NoResultFound:
            sv = bdosoa.model.SubscriptionVersion.create(
                spid=msg_obj.service_prov_id,
                subscription_version_id=tn_version_id.version_id)

            self.logger('New subscription version: {0}'.format(
                tn_version_id.version_id), msg_obj)

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
        sv.subscription_download_reason = data.subscription_download_reason
        sv.subscription_line_type = data.subscription_line_type
        sv.subscription_optional_data = data.subscription_optional_data

        return msg_obj.reply()

    def process_sv_delete_download(self, msg_obj):
        """Remove a subscription version

        :param SVDeleteDownload msg_obj: SVDeleteDownload message
        """

        version_id = msg_obj.message_content.subscription_version_id

        try:
            sv = bdosoa.model.SubscriptionVersion.get_by(
                spid=msg_obj.service_prov_id,
                subscription_version_id=version_id,
            )

            bdosoa.model.meta.Session.delete(sv)

            self.logger('Removed subscription version: {0}'
                        .format(version_id), msg_obj)

        except bdosoa.model.SubscriptionVersion.NoResultFound:
            self.logger('Subscription version not found: {0}'
                        .format(version_id), msg_obj)

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

        query_result = [
            libspg.SubscriptionVersionData(
                libspg.TNVersionId(
                    tn=sv.subscription_version_tn,
                    version_id=sv.subscription_version_id,
                ),
                libspg.SubscriptionData(
                    subscription_recipient_sp=sv.subscription_recipient_sp,
                    subscription_recipient_eot=sv.subscription_recipient_eot,
                    subscription_activation_timestamp=
                    sv.subscription_activation_timestamp,
                    broadcast_window_start_timestamp=
                    sv.subscription_broadcast_timestamp,
                    subscription_rn1=sv.subscription_rn1,
                    subscription_new_cnl=sv.subscription_new_cnl,
                    subscription_lnp_type=sv.subscription_lnp_type,
                    subscription_download_reason=
                    sv.subscription_download_reason,
                    subscription_line_type=sv.subscription_line_type,
                    subscription_optional_data=sv.subscription_optional_data,
                )
            )

            for sv in bdosoa.model.SubscriptionVersion.filter_by(
                spid=spid).filter(query_string).all() if query_string
        ]

        self.logger('Query result: {0}'.format(
            list(sv.subscription_tn_version_id.version_id
                 for sv in query_result)), msg_obj)

        return msg_obj.reply(query_result)
