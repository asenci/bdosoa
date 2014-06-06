import cherrypy
from libspg import Message as MessageObj
from libspg.bdo import BDRtoBDO
from sqlalchemy.orm.exc import NoResultFound

from bdosoa.plugins import BDOSOAPlugin
from bdosoa.models.meta import Session
from bdosoa.models import ServiceProvider
from bdosoa.soap import SOAPApplication
from bdosoa.utils import config_logging


class SOAP(object):
    def __init__(self):
        self.soap_app = SOAPApplication('BDO/SoapServer')
        self.soap_app.register_method('processResponse', self.receive_soap)

    @cherrypy.expose
    def index(self, spid=None, token=None):
        if cherrypy.serving.request.method != 'POST':
            cherrypy.serving.response.headers['Allow'] = 'POST'
            raise cherrypy.HTTPError(405)

        try:
            cherrypy.request.service_provider = ServiceProvider.get_by(
                spid=spid, token=token, enabled=True)
        except NoResultFound:
            raise cherrypy.HTTPError(403)

        status_code, response = self.soap_app(cherrypy.request.body.read())

        cherrypy.response.status = status_code
        return response

    @staticmethod
    def receive_soap(_, message):
        """Receive SOAP request and enqueue message for processing"""

        # Get service provider instance for this request
        service_provider = cherrypy.serving.request.service_provider

        # Initialise message object from XML string
        msg_obj = MessageObj.from_string(message)

        # Compare message service provider ID with the provided token
        if msg_obj.service_prov_id != service_provider.spid:
            raise ValueError(
                'Message SPID ({0}) does not match request SPID ({1})'
                .format(msg_obj.service_prov_id, service_provider.spid))

        # Only BDR to BDO messages are allowed
        if not isinstance(msg_obj, BDRtoBDO):
            raise TypeError('Invalid message type: {0}'.format(
                type(msg_obj).__name__))

        try:
            cherrypy.engine.publish('bdosoa-message', msg_obj, message)

        except:
            return '-1'

        return '0'


class Root(object):
    soap = SOAP().index

    @cherrypy.expose
    def index(self):
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return 'OK\n'


# Clean database session after request finishes processing
cherrypy.config.update({'hooks.on_end_resource': Session.cleanup_hook})

# Configuration handlers
cherrypy.config.namespaces['database'] = Session.config_handler
cherrypy.config.namespaces['add_log'] = lambda k, v: config_logging(v)

# Mount the main application
cherrypy.tree.mount(Root())

# Enable the message processing plugin
BDOSOAPlugin(cherrypy.engine).subscribe()
