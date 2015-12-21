"""
bdosoa - SOAP processing routines
"""

import logging
import urllib2

from lxml import etree
from lxml.builder import ElementMaker


#
# XML
#

SOAP_ENV_NS = 'soapenv'
SOAP_ENV_URI = 'http://schemas.xmlsoap.org/soap/envelope/'

SOAP_NSMAP = {
    SOAP_ENV_NS: SOAP_ENV_URI,
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}

QName = etree.QName


# noinspection PyDocstring
class ElementBase(etree.ElementBase):
    def __str__(self):
        return self.to_string(self)

    def __unicode__(self):
        return str(self).decode()

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


# noinspection PyDocstring
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


# noinspection PyDocstring
class SOAPEnvelope(SOAPElementBase):
    @property
    def header(self):
        return self.find('Header')

    @property
    def body(self):
        return self.find('Body')


# noinspection PyDocstring
class SOAPHeader(SOAPElementBase):
    pass


# noinspection PyDocstring
class SOAPBody(SOAPElementBase):
    @property
    def fault(self):
        return self.find('Fault')


# noinspection PyDocstring
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


XMLParserLookup.get_namespace(SOAP_ENV_URI)[None] = SOAPElementBase
XMLParserLookup.get_namespace(SOAP_ENV_URI)['Envelope'] = SOAPEnvelope
XMLParserLookup.get_namespace(SOAP_ENV_URI)['Header'] = SOAPHeader
XMLParserLookup.get_namespace(SOAP_ENV_URI)['Body'] = SOAPBody
XMLParserLookup.get_namespace(SOAP_ENV_URI)['Fault'] = SOAPFault


#
# Main classes
#

class SOAPException(Exception):
    """SOAP exception"""

    pass


class SOAPApplication(object):
    """SOAP application

    :param str namespace: Default namespace URI for registering methods
    """

    __methods__ = {}
    __namespace__ = ''

    def __init__(self, namespace=None):
        self.logger = logging.getLogger(
            '.'.join([__name__, self.__class__.__name__]))

        if namespace is not None:
            self.__namespace__ = namespace

    def process_request(self, request):
        """Process SOAP requests

        :param str request: XML document
        :return: A tuple consisting in the response code and the response body
        :rtype: tuple
        """

        try:
            self.logger.debug('Received SOAP request:\n{0}'.format(request))

            # Deserialize the request
            soap_request = ElementBase.from_string(request)

            # Initialize the response
            soap_response = S.Envelope(S.Body())

            for method_call in soap_request.body:

                method = self.__methods__.get(method_call.tag)

                if method is None:
                    raise NotImplementedError(
                        'Method not implemented: {0}'.format(method_call.tag))

                params = dict((QName(arg).localname, arg.text)
                              for arg in method_call)

                result = method(**params)

                soap_response.body.append(
                    E(method_call.tag + 'Response',
                      E(method_call.tag + 'Result', result))
                )

        except:
            soap_response = S.Envelope(S.Body(
                S.Fault(
                    E.faultcode(':'.join([SOAP_ENV_NS, 'Server'])),
                    E.faultstring('Error processing the request')
                )
            ))

        # Serialize the response
        response_body = str(soap_response)

        self.logger.debug('Request response:\n({0})\n{1}'.format(
            response_code, response_body))

        return response_code, response_body

    def register_method(self, name, func):
        """Register application method

        :param str name: Method name
        :param function func: Target callable
        """

        if isinstance(name, (str, unicode)) and not name.startswith('{'):
            name = QName(self.__namespace__, name).text

        self.__methods__[name] = func


class SOAPClient(object):
    """SOAP client

    :param str url: Request URL
    :param str namespace: Target namespace
    """
    __url__ = ''
    __namespace__ = ''

    def __init__(self, url, namespace=None):
        self.logger = logging.getLogger(
            '.'.join([__name__, self.__class__.__name__]))

        self.__url__ = url

        if namespace is not None:
            self.__namespace__ = namespace

    def __getattr__(self, method):

        # noinspection PyDocstring
        def method_call(**kwargs):

            # Build the SOAP request
            soap_request = S.Envelope(
                S.Body(
                    E(QName(self.__namespace__, method), *[
                        E(QName(self.__namespace__, key), value) for
                        key, value in kwargs.items()
                    ])
                )
            )

            # Serialize the request
            request = str(soap_request)

            self.logger.debug('Sending SOAP request:\n{0}'.format(request))

            try:
                request = urllib2.urlopen(urllib2.Request(
                    self.__url__, request, headers={
                        'Content-Type': 'text/xml; charset=utf-8',
                        'Soapaction': 'urn:{0}'.format(method),
                    }),
                )

                response = request.read()

            except urllib2.HTTPError as e:
                response = e.read()

            self.logger.debug('Received response:\n{0}'.format(response))

            # Deserialize the response
            soap_response = ElementBase.from_string(response)

            if isinstance(soap_response.body, SOAPFault):
                raise SOAPException(soap_response.body.fault_string)

            method_response = soap_response.body.find(
                QName(self.__namespace__, method + 'Response'))

            return tuple(result.text for result in method_response)

        return method_call
