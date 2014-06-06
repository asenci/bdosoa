import logging
import urllib2

from lxml import etree
from lxml.builder import ElementMaker


#
# XML
#

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
            string = string.encode()

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


class SOAPEnvelope(SOAPElementBase):
    @property
    def header(self):
        return self.find('Header')

    @property
    def body(self):
        return self.find('Body')


class SOAPHeader(SOAPElementBase):
    pass


class SOAPBody(SOAPElementBase):
    @property
    def fault(self):
        return self.find('Fault')


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
    pass


class SOAPApplication(object):
    __methods__ = {}
    __namespace__ = ''

    def __init__(self, namespace_uri=None):
        self.log = logging.getLogger(
            '.'.join([__name__, self.__class__.__name__]))

        if namespace_uri is not None:
            self.__namespace__ = namespace_uri

    def __call__(self, request):
        fault = False

        try:
            self.log.debug('Received SOAP request:\n{0}'.format(request))

            # Deserialize the request
            soap_request = ElementBase.from_string(request)

            # Initialize the response
            soap_response = S.Envelope(S.Body())

            # Process each call in the request
            for call in soap_request.body:

                # Get registered method
                method = self.__methods__.get(call.tag, None)

                if method is None:
                    raise SOAPException(
                        'Method not implemented: {0}'.format(call.tag))

                elif callable(method):
                    # Call method with arguments
                    result = method(*(arg.text for arg in call))

                    # Append result to the response
                    soap_response.body.append(
                        E(call.tag + 'Response',
                          E(call.tag + 'Result', result))
                    )

                else:
                    raise SOAPException(
                        'The registered method is not callable: {0}'.format(
                            call.tag))

        except Exception as e:
            self.log.exception('Error processing the request.')

            # Generate a SOAP Fault message
            soap_response = S.Envelope(S.Body(S.Fault(
                E.faultcode(':'.join(['soapenv', 'Client'])),
                E.faultstring(str(e))
            )))

            fault = True

        # Serialize the response
        response = str(soap_response)

        self.log.debug('Sending SOAP response:\n{0}'.format(response))
        return 500 if fault else 200, response

    def register_method(self, name, method):
        if isinstance(name, (str, unicode)) and name[0] not in ['{', '/', '.']:
            name = QName(self.__namespace__, name).text
        self.__methods__[name] = method


class SOAPClient(object):
    __url__ = ''
    __namespace__ = ''

    def __init__(self, url, namespace_uri=None):
        self.log = logging.getLogger(
            '.'.join([__name__, self.__class__.__name__]))

        self.__url__ = url

        if namespace_uri is not None:
            self.__namespace__ = namespace_uri

    def __getattr__(self, method):
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

            request = str(soap_request)
            self.log.debug('Sending SOAP request:\n{0}'.format(request))

            # Try to send the request
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

            self.log.debug('Received response:\n{0}'.format(response))

            # Deserialize the response
            soap_response = ElementBase.from_string(response)

            if isinstance(soap_response.body, SOAPFault):
                raise SOAPException(soap_response.body.fault_string)

            # Get the response
            method_response = soap_response.body.find(
                QName(self.__namespace__, method + 'Response'))

            # Return the results
            return tuple(result.text for result in method_response)

        return method_call
