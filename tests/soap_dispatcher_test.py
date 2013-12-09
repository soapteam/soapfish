
from __future__ import absolute_import

from lxml import etree

from soapbox import soap, xsd
from soapbox.soap_dispatch import SOAPDispatcher, SoapboxRequest
from soapbox.lib.pythonic_testcase import *
from soapbox.lib.attribute_dict import AttrDict
from soapbox.soap import SOAPError


class SoapDispatcherTest(PythonicTestCase):
    def test_can_dispatch_good_soap_message(self):
        handler, handler_state = self._echo_handler()
        request = SoapboxRequest(None, dict(SOAPACTION='echo'), 'POST')
        dispatcher = SOAPDispatcher(self._echo_service(handler))
        
        soap_message = ('<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<value>foobar</value>'
        '</ns1:echoRequest>')
        request_message = self._wrap_with_soap_envelope(soap_message)
        response = dispatcher.dispatch(request, request_message)
        self.assert_is_successful_response(response, handler_state)
        assert_equals('foobar', handler_state.input_.value)
        
        response_document = etree.fromstring(response.message)
        response_xml = etree.tostring(response_document, pretty_print=True)
        expected_xml = (
            '<ns0:Envelope xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/">\n'
            '  <ns0:Body>\n'
            '    <ns0:echoResponse xmlns:ns0="http://soap.example/echo/types">\n'
            '      <value>foobar</value>\n'
            '    </ns0:echoResponse>\n'
            '  </ns0:Body>\n'
            '</ns0:Envelope>\n'
        )
        assert_equals(expected_xml, response_xml)
    
    def test_can_validate_soap_message(self):
        handler, handler_state = self._echo_handler()
        request = SoapboxRequest(None, dict(SOAPACTION='echo'), 'POST')
        dispatcher = SOAPDispatcher(self._echo_service(handler))
        
        soap_message = ('<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<invalid>foobar</invalid>'
        '</ns1:echoRequest>')
        request_message = self._wrap_with_soap_envelope(soap_message)
        response = dispatcher.dispatch(request, request_message)
        assert_false(handler_state.was_called)
        self.assert_is_soap_fault(response,
            partial_fault_string=u"Element 'invalid': This element is not expected. Expected is ( value ).")
    
    def test_can_reject_malformed_xml_soap_message(self):
        request = SoapboxRequest(None, dict(), 'POST')
        dispatcher = SOAPDispatcher(self._echo_service())
        
        response = dispatcher.dispatch(request, 'garbage')
        assert_equals(500, response.status)
        assert_equals('text/xml', response.content_type)
        self.assert_is_soap_fault(response, partial_fault_string=u"Start tag expected, '<' not found")
    
    def test_can_dispatch_requests_based_on_soap_body(self):
        handler, handler_state = self._echo_handler()
        request = SoapboxRequest(None, dict(SOAPACTION='""'), 'POST')
        dispatcher = SOAPDispatcher(self._echo_service(handler))
        
        soap_message = ('<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<value>foobar</value>'
        '</ns1:echoRequest>')
        request_message = self._wrap_with_soap_envelope(soap_message)
        response = dispatcher.dispatch(request, request_message)
        self.assert_is_successful_response(response, handler_state)
    
    def test_can_use_soap_error_from_handler(self):
        request = SoapboxRequest(None, dict(), 'POST')
        faulty_handler = self._faulty_handler()
        dispatcher = SOAPDispatcher(self._echo_service(handler=faulty_handler))
        
        soap_message = ('<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<value>foobar</value>'
        '</ns1:echoRequest>')
        request_message = self._wrap_with_soap_envelope(soap_message)
        response = dispatcher.dispatch(request, request_message)
        assert_equals('text/xml', response.content_type)
        assert_equals(500, response.status)
        self.assert_is_soap_fault(response,
            fault_code='foobar',
            partial_fault_string=u'internal data error'
        )
    
    # --- custom assertions ---------------------------------------------------
    
    def assert_is_successful_response(self, response, handler_state=None):
        assert_equals(200, response.status)
        assert_equals('text/xml', response.content_type)
        if handler_state:
            assert_true(handler_state.was_called)
    
    def assert_is_soap_fault(self, response, fault_code=None, partial_fault_string=None):
        assert_equals(500, response.status)
        assert_equals('text/xml', response.content_type)
        
        fault_document = etree.fromstring(response.message)
        soap_envelope = fault_document.getroottree()
        namespaces = {'s': 'http://schemas.xmlsoap.org/soap/envelope/'}
        fault_nodes = soap_envelope.xpath('/s:Envelope/s:Body/s:Fault', namespaces=namespaces)
        assert_length(1, fault_nodes, message='expected exactly one SOAP fault')
        children = list(fault_nodes[0])
        assert_length(2, children)
        
        xml_fault_code, fault_string = children
        if fault_code is None:
            fault_code = 'Client'
        assert_equals(fault_code, xml_fault_code.text)
        if partial_fault_string:
            assert_contains(partial_fault_string, fault_string.text)
    
    # --- internal helpers ----------------------------------------------------
    
    def _wrap_with_soap_envelope(self, payload):
        return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<senv:Envelope xmlns:senv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://soap.example/echo/types">'
            '<senv:Body>%(payload)s</senv:Body>'
            '</senv:Envelope>'
        ) % dict(payload=payload)
    
    # --- define test service -------------------------------------------------
    class EchoType(xsd.ComplexType):
        INHERITANCE = None
        INDICATOR = xsd.Sequence
        value = xsd.Element('String', nillable=False)
        
        @classmethod
        def create(cls, value):
            instance = cls()
            instance.value = value
            return instance
    
    def _echo_handler(self):
        state = AttrDict(was_called=False)
        def _handler(request, input_):
            state.update(dict(
                was_called = True,
                request = request,
                input_ = input_
            ))
            return self.EchoType.create(input_.value)
        return _handler, state
    
    def _echo_service(self, handler=None):
        if handler is None:
            handler, handler_state = self._echo_handler()
        
        EchoSchema = xsd.Schema(
            'http://soap.example/echo/types',
            elementFormDefault=xsd.ElementFormDefault.UNQUALIFIED,
            complexTypes=(self.EchoType,),
            elements={
                'echoRequest': xsd.Element('EchoType'),
                'echoResponse': xsd.Element('EchoType'),
            },
        )
        echo_method = xsd.Method(function=handler,
            soapAction='echo',
            input='echoRequest',
            inputPartName='input_',
            output='echoResponse',
            outputPartName='result',
            operationName='echoOperation',
        )
        return soap.Service(
            name='TestService',
            targetNamespace='http://soap.example/echo',
            location='http://soap.example/ws',
            schema=EchoSchema,
            version=soap.SOAPVersion.SOAP11,
            methods=[echo_method]
        )
    
    def _faulty_handler(self):
        soap_error = SOAPError('some error', 'foobar', 'internal data error')
        return lambda request, input_: soap_error
