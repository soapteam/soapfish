import unittest

from soapbox import xsd
from soapbox import soap11
from soapbox import soap12
from soapbox.lib.pythonic_testcase import *

SOAP11_ENVELOPE = """\
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    {0}<soap:Body>{1}</soap:Body>
</soap:Envelope>
"""

SOAP11_FAULT = """
<soap:Fault>
    <faultcode>soap:Server</faultcode>
    <faultstring>Server was unable to process request.</faultstring>
    <detail />
</soap:Fault>
"""

MESSAGE_QUALIFIED = """
<ns0:GetWeatherByPlaceName xmlns:ns0="http://www.example.org">
    <ns0:Place><ns0:Name>Weatharia</ns0:Name></ns0:Place>
</ns0:GetWeatherByPlaceName>
"""

MESSAGE_UNQUALIFIED = """
<ns0:GetWeatherByPlaceName xmlns:ns0="http://www.example.org">
    <Place><Name>Weatharia</Name></Place>
</ns0:GetWeatherByPlaceName>
"""

class Place(xsd.ComplexType):
    Name = xsd.Element(xsd.String)

class GetWeatherByPlaceName(xsd.ComplexType):
    Place = xsd.Element(Place)

class AppHeader(xsd.ComplexType):
    Version = xsd.Element(xsd.String)
    Message = xsd.Element(GetWeatherByPlaceName)

Schema_qualified = xsd.Schema(
    targetNamespace='http://www.example.org',
    elementFormDefault=xsd.ElementFormDefault.QUALIFIED,
    complexTypes=[GetWeatherByPlaceName, AppHeader, Place],
    elements={
        'GetWeatherByPlaceName': xsd.Element(GetWeatherByPlaceName),
        'AppHeader': xsd.Element(AppHeader),
    },
)

class PlaceU(xsd.ComplexType):
    Name = xsd.Element(xsd.String)

class GetWeatherByPlaceNameU(xsd.ComplexType):
    Place = xsd.Element(PlaceU)

class AppHeaderU(xsd.ComplexType):
    Version = xsd.Element(xsd.String)
    Message = xsd.Element(GetWeatherByPlaceNameU)

Schema_unqualified = xsd.Schema(
    targetNamespace='http://www.example.org',
    complexTypes=[GetWeatherByPlaceNameU, AppHeaderU, PlaceU],
    elements={
        'GetWeatherByPlaceName': xsd.Element(GetWeatherByPlaceNameU),
        'AppHeader': xsd.Element(AppHeaderU),
    },
)


class SOAP_TBase(object):

    def test_parse_message_qualified(self):
        self._test_parse_message(MESSAGE_QUALIFIED, GetWeatherByPlaceName, Schema_qualified)

    def test_parse_message_unqualified(self):
        self._test_parse_message(MESSAGE_UNQUALIFIED, GetWeatherByPlaceNameU, Schema_unqualified)

    def _test_parse_message(self, xml, MessageType, schema):
        envelope = self.SOAP.Envelope.parsexml(self.ENVELOPE_XML.format('', xml).encode('utf8'))
        message = MessageType.parsexml(envelope.Body.content(), schema)
        self.assertEqual(message.Place.Name, 'Weatharia')
        message = envelope.Body.parse_as(MessageType)
        self.assertEqual(message.Place.Name, 'Weatharia')

    def test_render_message_qualified(self):
        self._test_render_message(GetWeatherByPlaceName, Place, Schema_qualified)

    def test_render_message_unqualified(self):
        self._test_render_message(GetWeatherByPlaceNameU, PlaceU, Schema_unqualified)

    def _test_render_message(self, MessageType, PlaceType, schema):
        return_object = MessageType(Place=PlaceType(Name='Skypia'))
        xml = self.SOAP.Envelope.response('GetWeatherByPlaceName', return_object)
        envelope = self.SOAP.Envelope.parsexml(xml)
        message = MessageType.parsexml(envelope.Body.content(), schema)
        self.assertEqual(message.Place.Name, 'Skypia')
        message = envelope.Body.parse_as(MessageType)
        self.assertEqual(message.Place.Name, 'Skypia')

    def test_header_qualified(self):
        self._test_header(GetWeatherByPlaceName, Place, AppHeader)

    def test_header_unqualified(self):
        self._test_header(GetWeatherByPlaceNameU, PlaceU, AppHeaderU)

    def _test_header(self, MessageType, PlaceType, HeaderType):
        message = MessageType(Place=PlaceType(Name='Skypia'))
        header = HeaderType(Version='1.0', Message=message)
        xml = self.SOAP.Envelope.response('GetWeatherByPlaceName', message, header)
        envelope = self.SOAP.Envelope.parsexml(xml)
        message = envelope.Header.parse_as(HeaderType)
        self.assertEqual(message.Version, '1.0')
        self.assertEqual(message.Message.Place.Name, 'Skypia')

    def test_empty_header(self):
        xml = self.SOAP.Envelope.response('Get', Place(), self.SOAP.Header())
        assert_contains(b'<ns0:Header/>', xml)

    def test_no_header_in_xml(self):
        xml = (b'<ns0:Envelope xmlns:ns0="http://www.w3.org/2003/05/soap-envelope">'
            b'<ns0:Body></ns0:Body>'
            b'</ns0:Envelope>')
        envelope = self.SOAP.Envelope.parsexml(xml)


class SOAP11_Test(SOAP_TBase, unittest.TestCase):

    SOAP = soap11
    ENVELOPE_XML = SOAP11_ENVELOPE

    def test_parse_fault(self):
        envelope = self.SOAP.Envelope.parsexml(self.ENVELOPE_XML.format('', SOAP11_FAULT).encode('utf8'))
        code, message, actor = self.SOAP.parse_fault_message(envelope.Body.Fault)
        self.assertEqual(message, 'Server was unable to process request.')
        self.assertEqual(code, 'soap:Server')

    def test_render_fault(self):
        xml = self.SOAP.Envelope.error_response('soap:Client', 'Go away.')
        envelope = self.SOAP.Envelope.parsexml(xml)
        code, message, actor = self.SOAP.parse_fault_message(envelope.Body.Fault)
        self.assertEqual(message, 'Go away.')
        self.assertEqual(code, 'soap:Client')


SOAP12_ENVELOPE = """\
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
    {0}<soap:Body>{1}</soap:Body>
</soap:Envelope>
"""

SOAP12_FAULT = """
<soap:Fault>
    <soap:Code>
        <soap:Value>soap:Receiver</soap:Value>
        <soap:Subcode>
            <soap:Value>ServerProxy</soap:Value>
        </soap:Subcode>
    </soap:Code>
    <soap:Reason>
        <soap:Text>Server was unable to process request. Go away.</soap:Text>
    </soap:Reason>
    <soap:Detail />
</soap:Fault>
"""


class SOAP12_Test(SOAP_TBase, unittest.TestCase):

    SOAP = soap12
    ENVELOPE_XML = SOAP12_ENVELOPE

    def test_parse_fault(self):
        envelope = self.SOAP.Envelope.parsexml(self.ENVELOPE_XML.format('', SOAP12_FAULT).encode('utf8'))
        code, message, actor = self.SOAP.parse_fault_message(envelope.Body.Fault)
        self.assertEqual(message, 'Server was unable to process request. Go away.')
        self.assertEqual(code, 'soap:Receiver')

    def test_render_fault(self):
        xml = self.SOAP.Envelope.error_response('soap:Sender', 'Go away.')
        envelope = self.SOAP.Envelope.parsexml(xml)
        code, message, actor = self.SOAP.parse_fault_message(envelope.Body.Fault)
        self.assertEqual(message, 'Go away.')
        self.assertEqual(code, 'soap:Sender')
