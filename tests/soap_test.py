import unittest

from lxml import etree

from soapfish import core, soap, soap11, soap12

SOAP11_ERROR_MESSAGE = '''
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
   <SOAP-ENV:Body>
      <SOAP-ENV:Fault>
         <faultcode>Result</faultcode>
         <faultstring/>
         <faultactor>Resultset empty2.</faultactor>
         <detail/>
      </SOAP-ENV:Fault>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
'''

SOAP11_ERROR_MESSAGE_NO_ACTOR = '''
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
   <SOAP-ENV:Body>
      <SOAP-ENV:Fault>
         <faultcode>Result</faultcode>
         <faultstring>String</faultstring>
         <detail/>
      </SOAP-ENV:Fault>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
'''

SOAP12_ERROR_ROLE = '''<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope">
<env:Header/><env:Body>
<env:Fault>
<env:Code><env:Value>env:Sender</env:Value></env:Code>
<env:Reason><env:Text xml:lang="en-US">
Message does not have necessary info
</env:Text></env:Reason>
<env:Role>http://gizmos.com/order</env:Role>
<env:Detail>
<PO:order xmlns:PO="http://gizmos.com/orders/">
Quantity element does not have a value</PO:order>
<PO:confirmation xmlns:PO="http://gizmos.com/confirm">
Incomplete address: no zip code</PO:confirmation>
</env:Detail></env:Fault>
</env:Body></env:Envelope>
'''

SOAP12_ERROR_NOROLE = '''<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope">
<env:Header/><env:Body>
<env:Fault>
<env:Code><env:Value>env:Sender</env:Value></env:Code>
<env:Reason><env:Text xml:lang="en-US">
Message does not have necessary info
</env:Text></env:Reason>
<env:Detail>
<PO:order xmlns:PO="http://gizmos.com/orders/">
Quantity element does not have a value</PO:order>
<PO:confirmation xmlns:PO="http://gizmos.com/confirm">
Incomplete address: no zip code</PO:confirmation>
</env:Detail></env:Fault>
</env:Body></env:Envelope>
'''


class ErrorHandling(unittest.TestCase):
    def test_soap11_actor_parsing(self):
        envelope = soap11.Envelope.parsexml(SOAP11_ERROR_MESSAGE)
        code, message, actor = soap11.parse_fault_message(envelope.Body.Fault)
        self.assertEqual('Result', code)
        self.assertIsNone(message)
        self.assertEqual('Resultset empty2.', actor)

    def test_soap11_noactor_parsing(self):
        envelope = soap11.Envelope.parsexml(SOAP11_ERROR_MESSAGE_NO_ACTOR)
        code, message, actor = soap11.parse_fault_message(envelope.Body.Fault)
        self.assertEqual('Result', code)
        self.assertEqual('String', message)
        self.assertIsNone(actor)

    def test_soap11_fault_handling(self):
        service = soap.Service(
            location='mock_location',
            methods=[],
            name=None,
            schemas=[],
            targetNamespace=None,
            version=soap.SOAPVersion.SOAP11,
        )
        stub = soap.Stub(location='empty', service=service)

        with self.assertRaises(core.SOAPError) as cm:
            stub._handle_response(None, None, SOAP11_ERROR_MESSAGE)
        self.assertEqual('Result', cm.exception.code)
        self.assertIsNone(cm.exception.message)
        self.assertEqual('Resultset empty2.', cm.exception.actor)

    def test_soap12_actor_parsing(self):
        envelope = soap12.Envelope.parsexml(SOAP12_ERROR_ROLE)
        code, message, actor = soap12.parse_fault_message(envelope.Body.Fault)
        self.assertEqual('env:Sender', code)
        self.assertEqual('\nMessage does not have necessary info\n', message)
        self.assertEqual('http://gizmos.com/order', actor)

    def test_soap12_noactor_parsing(self):
        envelope = soap12.Envelope.parsexml(SOAP12_ERROR_NOROLE)
        code, message, actor = soap12.parse_fault_message(envelope.Body.Fault)
        self.assertEqual('env:Sender', code)
        self.assertEqual('\nMessage does not have necessary info\n', message)
        self.assertIsNone(actor)

    def test_soap12_fault_handling(self):
        service = soap.Service(
            location='mock_location',
            methods=[],
            name=None,
            schemas=[],
            targetNamespace=None,
            version=soap.SOAPVersion.SOAP12,
        )
        stub = soap.Stub(location='empty', service=service)

        with self.assertRaises(core.SOAPError) as cm:
            stub._handle_response(None, None, SOAP12_ERROR_ROLE)
        self.assertEqual('env:Sender', cm.exception.code)
        self.assertEqual('\nMessage does not have necessary info\n', cm.exception.message)
        self.assertEqual('http://gizmos.com/order', cm.exception.actor)


class SOAPVersionTest(unittest.TestCase):
    WSDL = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<definitions '
        'xmlns:http="http://schemas.xmlsoap.org/wsdl/http/" '
        'xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" '
        'xmlns:soap12="http://schemas.xmlsoap.org/wsdl/soap12/" '
        'xmlns:s="http://www.w3.org/2001/XMLSchema" '
        'xmlns:s0="http://tempuri.org/encodedTypes" '
        'xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/" '
        'xmlns:tns="http://tempuri.org/" '
        'xmlns:tm="http://microsoft.com/wsdl/mime/textMatching/" '
        'xmlns:mime="http://schemas.xmlsoap.org/wsdl/mime/" '
        'targetNamespace="http://tempuri.org/" '
        'xmlns="http://schemas.xmlsoap.org/wsdl/">'
        '<binding name="HelloWorldSoap" type="tns:HelloWorldSoap">'
        '<{soap_version}:binding transport="http://schemas.xmlsoap.org/soap/http" style="document" />'
        '</binding>'
        '</definitions>'
    )

    def test_can_detect_soap12_from_xml(self):
        WSDL = self.WSDL.format(soap_version='soap12').encode()
        xml = etree.fromstring(WSDL)
        soap_version = soap.SOAPVersion.get_version_from_xml(xml)
        self.assertEqual(soap.SOAPVersion.SOAP12, soap_version)

    def test_can_detect_soap11_from_xml(self):
        WSDL = self.WSDL.format(soap_version='soap').encode()
        xml = etree.fromstring(WSDL)
        soap_version = soap.SOAPVersion.get_version_from_xml(xml)
        self.assertEqual(soap.SOAPVersion.SOAP11, soap_version)

    def test_get_version_soap11(self):
        v = soap.SOAPVersion.get_version(soap11.ENVELOPE_NAMESPACE)
        self.assertEqual(soap11.NAME, v.NAME)

        v = soap.SOAPVersion.get_version(soap11.BINDING_NAMESPACE)
        self.assertEqual(soap11.NAME, v.NAME)

    def test_get_version_soap12(self):
        v = soap.SOAPVersion.get_version(soap12.ENVELOPE_NAMESPACE)
        self.assertEqual(soap12.NAME, v.NAME)

        v = soap.SOAPVersion.get_version(soap12.BINDING_NAMESPACE)
        self.assertEqual(soap12.NAME, v.NAME)
