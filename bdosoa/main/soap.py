import logging
import urllib2

from django.http import HttpResponse, HttpResponseNotAllowed
from django.http.response import HttpResponseBase
from lxml import etree
from lxml.builder import ElementMaker
from urlparse import urlsplit


#
# XML
#

class ElementBase(etree.ElementBase):
    def __str__(self):
        return self.to_string(self)

    def __unicode__(self):
        return str(self).decode('utf-8')

    @staticmethod
    def from_string(string):
        """Create an Element object from a string"""

        # Avoid unicode strings with encoding declaration
        if isinstance(string, unicode):
            string = string.encode('utf-8')

        # Parse the XML string
        return etree.fromstring(string, parser=XMLParser)

    @staticmethod
    def to_string(element):
        if callable(element):
            element = element()

        return etree.tostring(
            element,
            encoding='utf-8',
            xml_declaration=True,
            pretty_print=True,
        )

SOAP_ENV_URI = 'http://schemas.xmlsoap.org/soap/envelope/'

SOAP_NSMAP = {
    'soapenv': SOAP_ENV_URI,
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}

QName = etree.QName

XMLParserLookup = etree.ElementNamespaceClassLookup(
    fallback=etree.ElementDefaultClassLookup(element=ElementBase))

XMLParser = etree.XMLParser(encoding='utf-8', no_network=False)
XMLParser.set_element_class_lookup(XMLParserLookup)

E = ElementMaker(
    nsmap=SOAP_NSMAP,
    makeelement=XMLParser.makeelement,
)

S = ElementMaker(
    namespace=SOAP_ENV_URI,
    nsmap=SOAP_NSMAP,
    makeelement=XMLParser.makeelement,
)

SPG = ElementMaker(
    namespace='SPG/SoapServer',
    makeelement=XMLParser.makeelement,
)


class SOAPElementBase(ElementBase):
    def find(self, path, namespaces=None):
        if isinstance(path, (str, unicode)) and path[0] not in ['{', '/', '.']:
            path = QName(SOAP_ENV_URI, path)

        return super(ElementBase, self).find(path, namespaces)

    def findall(self, path, namespaces=None):
        if isinstance(path, (str, unicode)) and path[0] not in ['{', '/', '.']:
            path = QName(SOAP_ENV_URI, path)

        return super(ElementBase, self).findall(path, namespaces)

    def findtext(self, path, default=None, namespaces=None):
        if isinstance(path, (str, unicode)) and path[0] not in ['{', '/', '.']:
            path = QName(SOAP_ENV_URI, path)

        return super(ElementBase, self).findtext(path, default, namespaces)

XMLParserLookup.get_namespace(SOAP_ENV_URI)[None] = SOAPElementBase


class SOAPEnvelope(SOAPElementBase):
    @property
    def header(self):
        return self.find('Header')

    @property
    def body(self):
        return self.find('Body')

XMLParserLookup.get_namespace(SOAP_ENV_URI)['Envelope'] = SOAPEnvelope


class SOAPHeader(SOAPElementBase):
    pass

XMLParserLookup.get_namespace(SOAP_ENV_URI)['Header'] = SOAPHeader


class SOAPBody(SOAPElementBase):
    @property
    def fault(self):
        return self.find('Fault')

XMLParserLookup.get_namespace(SOAP_ENV_URI)['Body'] = SOAPBody


class SOAPFault(SOAPElementBase):
    @property
    def fault_code(self):
        return self.find('faultcode')

    @property
    def fault_string(self):
        return self.find('faultstring')

    @property
    def fault_actor(self):
        return self.find('faultactor')

    @property
    def detail(self):
        return self.find('detail')

XMLParserLookup.get_namespace(SOAP_ENV_URI)['Fault'] = SOAPFault


class BDOSoapServer(ElementBase):
    def find(self, path, namespaces=None):
        if isinstance(path, (str, unicode)) and path[0] not in ['{', '/', '.']:
            path = QName('BDO/SoapServer', path)

        return super(ElementBase, self).find(path, namespaces)

    def findall(self, path, namespaces=None):
        if isinstance(path, (str, unicode)) and path[0] not in ['{', '/', '.']:
            path = QName('BDO/SoapServer', path)

        return super(ElementBase, self).findall(path, namespaces)

    def findtext(self, path, default=None, namespaces=None):
        if isinstance(path, (str, unicode)) and path[0] not in ['{', '/', '.']:
            path = QName('BDO/SoapServer', path)

        return super(ElementBase, self).findtext(path, default, namespaces)

XMLParserLookup.get_namespace('BDO/SoapServer')[None] = BDOSoapServer


class SPGSoapServer(ElementBase):
    def find(self, path, namespaces=None):
        if isinstance(path, (str, unicode)) and path[0] not in ['{', '/', '.']:
            path = QName('SPG/SoapServer', path)

        return super(ElementBase, self).find(path, namespaces)

    def findall(self, path, namespaces=None):
        if isinstance(path, (str, unicode)) and path[0] not in ['{', '/', '.']:
            path = QName('SPG/SoapServer', path)

        return super(ElementBase, self).findall(path, namespaces)

    def findtext(self, path, default=None, namespaces=None):
        if isinstance(path, (str, unicode)) and path[0] not in ['{', '/', '.']:
            path = QName('SPG/SoapServer', path)

        return super(ElementBase, self).findtext(path, default, namespaces)

XMLParserLookup.get_namespace('SPG/SoapServer')[None] = SPGSoapServer


#
# HTTP
#

class SOAPResponse(HttpResponse):
    def __init__(self, soap_env):
        if etree.iselement(soap_env):
            soap_env = str(soap_env)

        super(SOAPResponse, self).__init__(
            soap_env, content_type='text/xml; charset=utf-8')


class SOAPResponseFault(SOAPResponse):
    def __init__(self, faultcode, faultstring, faultactor=None, detail=None):

        soap_env = S.Envelope(
            S.Body(
                S.Fault(
                    E.faultcode(':'.join([SOAP_ENV_URI, faultcode])),
                    E.faultstring(faultstring),
                    E.faultactor(faultactor) if faultactor is not None else '',
                    E.detail(detail) if detail is not None else '',
                )
            )
        )

        super(SOAPResponseFault, self).__init__(soap_env)


#
# Main classes
#

class SOAPException(Exception):
    pass


class SOAPApplication(object):
    __methods__ = {}
    __namespace__ = ''

    def __init__(self, namespace_uri=''):
        if namespace_uri is not None:
            self.__namespace__ = namespace_uri

    def __call__(self, request, **kwargs):
        logger = logging.getLogger(
            '.'.join([__name__, self.__class__.__name__]))

        # Only POST allowed (no WSDL info)
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])

        host = request.get_host()

        try:
            logger.debug('Received SOAP envelop from "{0}": {1!r}'.format(
                host, request.body))

            soap_env = ElementBase.from_string(request.body)

            soap_response = S.Envelope(S.Body())

            for call in soap_env.body:
                try:
                    method = self.__methods__.get(call.tag)

                except KeyError:
                    raise SOAPException(
                        'Method not implemented: {0}'.format(call.tag))

                result = method(
                    *(arg.text for arg in call), _request=request, **kwargs)

                if isinstance(result, HttpResponseBase):
                    return result

                soap_response.body.append(
                    E(call.tag + 'Response', E(call.tag + 'Result', result))
                )

        except Exception as e:
            logger.exception(e)
            response = SOAPResponseFault('Client', str(e))

        else:
            response = SOAPResponse(soap_response)

        logger.debug('Sending SOAP envelop to "{0}": {1!r}'.format(
            host, response.content))

        return response

    def register_method(self, name, method):
        if isinstance(name, (str, unicode)) and name[0] not in ['{', '/', '.']:
            name = QName(self.__namespace__, name).text
        self.__methods__[name] = method


class SOAPClient(object):
    __url__ = ''
    __namespace__ = ''

    def __init__(self, url, namespace_uri=None):
        self.__url__ = url

        if namespace_uri is not None:
            self.__namespace__ = namespace_uri

    def __getattr__(self, method):
        def method_call(**kwargs):
            logger = logging.getLogger(
                '.'.join([__name__, self.__class__.__name__, method]))

            # Build SOAP Envelope
            soap_env = S.Envelope(
                S.Body(
                    E(QName(self.__namespace__, method), *[
                        E(QName(self.__namespace__, key), value) for
                        key, value in kwargs.items()
                    ])
                )
            )

            host = urlsplit(self.__url__).netloc

            try:

                logger.debug('Sending SOAP envelop to "{0}": {1!r}'.format(
                    host, soap_env))

                request = urllib2.urlopen(urllib2.Request(
                    self.__url__,
                    str(soap_env),
                    headers={
                        'Content-Type': 'text/xml; charset=utf-8',
                        'Soapaction': 'urn:{0}'.format(method),
                    }),
                )

                response = request.read()
                resp_code = request.code

            except urllib2.HTTPError as e:
                response = e.read()
                resp_code = e.code

                try:
                    ElementBase.from_string(response)

                except Exception:
                    raise e

            logger.debug('Received SOAP envelop from "{0}": {1!r}'.format(
                host, response))

            soap_reply = ElementBase.from_string(response)

            if resp_code != 200:
                if isinstance(soap_reply.body, SOAPFault):
                    logger.error(soap_reply.body.fault_string)

                    raise SOAPException(soap_reply.body.fault_string)

                else:
                    logger.error('Invalid response from "{0}": {1!r}'.format(
                        host, response))
                    raise SOAPException(response)

            method_response = soap_reply.body.find(
                QName(self.__namespace__, method + 'Response'))

            return tuple(result.text for result in method_response)

        return method_call

