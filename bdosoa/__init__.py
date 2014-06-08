import cherrypy

# Database configuration
from bdosoa.models.meta import Session
cherrypy.config.namespaces['database'] = Session.config_handler

# Enable logging for other modules
from bdosoa.utils import config_logging as _config_logging
cherrypy.config.namespaces['add_log'] = lambda k, v: _config_logging(v)

# Enable the message processing plugin
from bdosoa.plugins import BDOSOAPlugin as _BDOSOAPlugin
cherrypy.engine.bdosoa = _BDOSOAPlugin(cherrypy.engine)


@cherrypy.popargs('command')
class API(object):

    @cherrypy.expose
    def index(self, command=None):
        if cherrypy.request.remote.ip == '127.0.0.1':
            if command == 'load_stalled':
                cherrypy.engine.bdosoa.load_stalled()
        else:
            raise cherrypy.HTTPError(403)


class Root(object):

    @cherrypy.expose
    def index(self):
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return 'OK\n'


@cherrypy.popargs('spid', 'token')
class SOAP(object):
    def __init__(self):
        from bdosoa.soap import SOAPApplication
        self.soap_app = SOAPApplication('BDO/SoapServer')
        self.soap_app.register_method('processResponse', self.receive_soap)

    @cherrypy.expose
    def index(self, spid=None, token=None):
        from bdosoa.models import ServiceProvider

        if cherrypy.request.method != 'POST':
            cherrypy.response.headers['Allow'] = 'POST'
            raise cherrypy.HTTPError(405)

        try:
            cherrypy.request.service_provider = ServiceProvider.get_by(
                spid=spid, token=token, enabled=True)
        except ServiceProvider.NoResultFound:
            raise cherrypy.HTTPError(403)

        status_code, response = self.soap_app(cherrypy.request.body.read())

        cherrypy.response.status = status_code
        return response

    @staticmethod
    def receive_soap(_, message):
        from libspg import Message as MessageObj
        from libspg.bdo import BDRtoBDO

        """Receive SOAP request and enqueue message for processing"""

        # Get service provider instance for this request
        service_provider = cherrypy.request.service_provider

        # Initialise message object from XML string
        msg_obj = MessageObj.from_string(message)

        # Compare message service provider ID with the provided token
        if msg_obj.service_prov_id != service_provider.spid:
            raise ValueError(
                'Message SPID ({0}) does not match request SPID ({1})'
                .format(msg_obj.service_prov_id, service_provider.spid))

        # Only BDR to BDO messages are allowed
        if not isinstance(msg_obj, BDRtoBDO):
            raise TypeError('Invalid message: {0!r}'.format(msg_obj))

        try:
            cherrypy.engine.publish('bdosoa-message', msg_obj, message)

        except:
            return '-1'

        return '0'
