import sys
import traceback
from Queue import Empty, Queue
from threading import Thread

import cherrypy
import libspg.bdo
from libspg import Message as MessageObj
from sqlalchemy.orm.exc import NoResultFound

from bdosoa.models import Message, ServiceProvider, SubscriptionVersion
from bdosoa.models.meta import Session
from bdosoa.soap import SOAPClient


class BDOSOAPlugin(cherrypy.process.plugins.SimplePlugin):
    """Message processing plugin for the BDOSOA application"""

    def __init__(self, bus):
        super(BDOSOAPlugin, self).__init__(bus)

        self.receiving = False
        self.receiver_queue = None
        self.receiver_thread = None
        
        self.working = False
        self.worker_queue = None
        self.worker_thread = None

        # Handlers for each message type
        self.MESSAGE_HANDLERS = {
            libspg.bdo.BDRError: lambda x: None,
            libspg.bdo.QueryBdoSVs: self.process_query_bdo_svs,
            libspg.bdo.SVCreateDownload: self.process_sv_create_download,
            libspg.bdo.SVDeleteDownload: self.process_sv_delete_download,
            libspg.bdo.SVQueryReply: lambda x: None,
        }

    def start(self):
        self.bus.log('Starting message processing plugin.', level=10)

        self.receiving = True
        self.receiver_queue = Queue()
        self.receiver_thread = Thread(target=self.receiver,
                                      name='BDOSOAReceiverThread')

        self.working = True
        self.worker_queue = Queue()
        self.worker_thread = Thread(target=self.worker,
                                    name='BDOSOAWorkerThread')

        # Start the receiver thread
        self.receiver_thread.start()

        # Start the worker thread
        self.worker_thread.start()

        # Load stalled messages into the queue
        self.load_stalled()

        self.bus.subscribe('bdosoa-message', self.queue_message)

        self.bus.log('Started message processing plugin.')
    start.priority = 70

    def stop(self):
        self.bus.log('Stopping message processing plugin.', level=10)

        self.bus.unsubscribe('bdosoa-message', self.queue_message)

        # Stop waiting for new messages
        self.receiving = False

        # Stop processing new messages
        self.working = False

        # Finish recording the last message on the database
        self.bus.log('Waiting for the receiver thread.')
        self.receiver_thread.join()

        # Finish processing the last message
        self.bus.log('Waiting for the worker thread.')
        self.worker_thread.join()

        self.bus.log('Stopped message processing plugin.')

    def graceful(self):
        self.stop()
        self.start()

    def load_stalled(self):
        self.bus.log('Loading stalled messages into queue.', level=10)

        stalled = Message.filter_by(done=False)
        Session.remove()

        for msg_log in stalled:
            msg_obj = MessageObj.from_string(msg_log.message_body)
            self.worker_queue.put((msg_obj, msg_log.id))
            self.bus.log('[{0}|{1}] Loaded message: {2}'
                         .format(msg_obj.invoke_id,
                                 msg_obj.service_prov_id,
                                 msg_log.id),
                         level=10)

    def queue_message(self, msg_obj, msg_txt):
        self.receiver_queue.put((msg_obj, msg_txt))
        self.bus.log('[{0}|{1}] Received message: {2!r}'.format(
            msg_obj.invoke_id, msg_obj.service_prov_id, msg_obj), level=10)

    def receiver(self):
        self.bus.log('Starting the receiver thread.', level=10)

        # Workaround for children thread receiving the same Request object
        # causing the database to be bind to the same object on all threads
        cherrypy.serving.request = object()

        while self.receiving:
            try:
                msg_obj, msg_txt = self.receiver_queue.get(timeout=1)
            except Empty:
                continue

            try:
                msg_log = Message.create(
                    service_provider_id=msg_obj.service_prov_id,
                    message_date_time=msg_obj.message_date_time,
                    invoke_id=msg_obj.invoke_id,
                    message_body=msg_txt,
                )
                Session.commit()
            except:
                Session.rollback()
                raise
            else:
                self.worker_queue.put((msg_obj, msg_log.id))
                self.bus.log('[{0}|{1}] Message added to the queue.'.format(
                    msg_obj.invoke_id, msg_obj.service_prov_id), level=10)
            finally:
                Session.remove()
                self.receiver_queue.task_done()

        else:
            self.bus.log('Stopped the receiver thread.', level=10)

    def worker(self):
        self.bus.log('Starting the worker thread.', level=10)

        # Workaround for children thread receiving the same Request object
        # causing the database to be bind to the same object on all threads
        cherrypy.serving.request = object()

        while self.working:
            try:
                msg_obj, msg_log_id = self.worker_queue.get(timeout=1)
            except Empty:
                continue

            self.bus.log('[{0}|{1}] Processing message.'.format(
                msg_obj.invoke_id, msg_obj.service_prov_id), level=10)

            try:
                self.process_message(msg_obj, msg_log_id)
                Session.commit()
            except:
                Session.rollback()
                raise
            finally:
                Session.remove()
                self.worker_queue.task_done()

            self.bus.log('[{0}|{1}] Finished processing message.'.format(
                msg_obj.invoke_id, msg_obj.service_prov_id), level=10)

        else:
            self.bus.log('Stopped the worker thread.', level=10)

    def process_message(self, msg_obj, msg_log_id):
        msg_log = Message.get(msg_log_id)

        try:
            # BDR to BDO
            if isinstance(msg_obj, libspg.bdo.BDRtoBDO):
                self.process_bdr_to_bdo(msg_obj)

            # BDO to BDR
            elif isinstance(msg_obj, libspg.bdo.BDOtoBDR):
                self.process_bdo_to_bdr(msg_obj)

            else:
                raise TypeError(
                    'Invalid message: {0!r}'.format(msg_obj))

        except:
            self.bus.log('[{0}|{1}] Error processing message.'
                         .format(msg_obj.invoke_id, msg_obj.service_prov_id),
                         traceback=True)

            # Stop processing messages
            self.working = False

            # Record error on the database
            msg_log.error = True
            msg_log.error_info += ''.join(
                traceback.format_exception(*sys.exc_info()) + ['\n\n'])

        else:
            msg_log.error = False
            msg_log.done = True

    def process_bdr_to_bdo(self, msg_obj):
        # Try to find a handler for the message type
        try:
            handler = self.MESSAGE_HANDLERS.get(type(msg_obj))

            self.bus.log('[{0}|{1}] Handler: {2!r}'
                         .format(msg_obj.invoke_id,
                                 msg_obj.service_prov_id,
                                 handler),
                         level=10)

        except KeyError:
            raise TypeError(
                'No handler for message: {0!r}'.format(msg_obj))

        # Invoke handler
        reply_obj = handler(msg_obj)

        # Enqueue reply if any
        if reply_obj is not None:
            self.bus.log(
                '[{0}|{1}] Handler generated reply: {2!r}'
                .format(msg_obj.invoke_id, msg_obj.service_prov_id, reply_obj),
                level=10)

            cherrypy.engine.publish('bdosoa-message',
                                    reply_obj,
                                    str(reply_obj))

    def process_bdo_to_bdr(self, msg_obj):
        service_provider = ServiceProvider.get_by(spid=msg_obj.service_prov_id)

        if not service_provider.enabled:
            self.bus.log('[{0}|{1}] Service provider disabled.'
                         .format(msg_obj.invoke_id, msg_obj.service_prov_id),
                         level=30)
            return

        elif not service_provider.spg_url:
            self.bus.log('[{0}|{1}] No SPG url for the service provider.'
                         .format(msg_obj.invoke_id, msg_obj.service_prov_id),
                         level=10)
            return

        self.bus.log('[{0}|{1}] Sending reply to: {2}'
                     .format(msg_obj.invoke_id,
                             msg_obj.service_prov_id,
                             service_provider.spg_url),
                     level=10)

        soap_client = SOAPClient(service_provider.spg_url, 'SPG/SoapServer')

        header = '{0}|{1}|{2:%s}'.format(
            msg_obj.service_prov_id,
            msg_obj.invoke_id,
            msg_obj.message_date_time,
        )

        result = soap_client.processRequest(
            header=header, message=str(msg_obj))

        if not result[0] == '0':
            raise ValueError(
                'Received "{0}" from SPG'.format(result))

    def process_sv_create_download(self, msg_obj):
        tn_version_id = msg_obj.message_content.subscription_tn_version_id
        data = msg_obj.message_content.subscription_data
        sv = None

        attrs = dict(
            subscription_version_tn=tn_version_id.tn,
            subscription_recipient_sp=data.subscription_recipient_sp,
            subscription_recipient_eot=data.subscription_recipient_eot,
            subscription_activation_timestamp=data.subscription_activation_timestamp,
            subscription_rn1=data.subscription_rn1,
            subscription_new_cnl=data.subscription_new_cnl,
            subscription_lnp_type=data.subscription_lnp_type,
            subscription_download_reason=data.subscription_download_reason,
            subscription_line_type=data.subscription_line_type,
            subscription_optional_data=data.subscription_optional_data
        )

        if data.broadcast_window_start_timestamp:
            attrs['subscription_broadcast_timestamp'] = \
                data.broadcast_window_start_timestamp

        try:
            sv = SubscriptionVersion.get_by(
                service_provider_id=msg_obj.service_prov_id,
                subscription_version_id=tn_version_id.version_id)

            self.bus.log('[{0}|{1}] Updating subscription version: {2}'
                         .format(msg_obj.invoke_id,
                                 msg_obj.service_prov_id,
                                 tn_version_id.version_id),
                         level=10)

        except NoResultFound:
            sv = SubscriptionVersion.create(
                service_provider_id=msg_obj.service_prov_id,
                subscription_version_id=tn_version_id.version_id)

            self.bus.log('[{0}|{1}] Creating subscription version: {2}'
                         .format(msg_obj.invoke_id,
                                 msg_obj.service_prov_id,
                                 tn_version_id.version_id),
                         level=10)

        finally:
            for key, value in attrs.items():
                setattr(sv, key, value)

        return msg_obj.reply()

    def process_sv_delete_download(self, msg_obj):
        version_id = msg_obj.message_content.subscription_version_id
        data = msg_obj.message_content.subscription_delete_data

        try:
            sv = SubscriptionVersion.get_by(
                service_provider_id=msg_obj.service_prov_id,
                subscription_version_id=version_id,
            )

            self.bus.log('[{0}|{1}] Updating subscription version: {2}'
                         .format(msg_obj.invoke_id,
                                 msg_obj.service_prov_id,
                                 version_id),
                         level=10)

        except NoResultFound:
            self.bus.log('[{0}|{1}] Subscription version not found: {2}'
                         .format(msg_obj.invoke_id,
                                 msg_obj.service_prov_id,
                                 version_id),
                         level=10)
            return

        sv.subscription_download_reason = data.subscription_download_reason
        sv.subscription_deletion_timestamp = msg_obj.message_date_time

        return msg_obj.reply()

    def process_query_bdo_svs(self, msg_obj):
        query = msg_obj.message_content.query_expression
        query = query.lstrip('"').rstrip('"')

        self.bus.log(
            '[{0}|{1}] Query string: {2}'
            .format(msg_obj.invoke_id, msg_obj.service_prov_id, query),
            level=10)

        reply_list = []
        sv_list = []

        if query:
            sv_list = SubscriptionVersion.filter_by(
                service_provider_id=msg_obj.service_prov_id
            ).filter(
                SubscriptionVersion.subscription_deletion_timestamp.is_(None)
            ).filter(
                query
            ).all()

        for sv in sv_list:
            sv_obj = libspg.SubscriptionVersionData(
                libspg.TNVersionId(
                    tn=sv.subscription_version_tn,
                    version_id=sv.subscription_version_id
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

            reply_list.append(sv_obj)

        self.bus.log(
            '[{0}|{1}] Query result: {2}'
            .format(msg_obj.invoke_id, msg_obj.service_prov_id,
                    [sv.subscription_tn_version_id.version_id
                     for sv in reply_list]),
            level=10)

        return msg_obj.reply(reply_list)
