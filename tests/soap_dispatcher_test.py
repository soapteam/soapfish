
from __future__ import absolute_import

import io
from lxml import etree
import six

from soapbox import soap, xsd
from soapbox.core import SoapboxRequest, SoapboxResponse
from soapbox.lib.pythonic_testcase import *
from soapbox.lib.attribute_dict import AttrDict
from soapbox.soap import SOAPError
from soapbox.soap_dispatch import SOAPDispatcher, WsgiSoapApplication


# --- define test service -------------------------------------------------
class EchoType(xsd.ComplexType):
    INHERITANCE = None
    INDICATOR = xsd.Sequence
    value = xsd.Element(xsd.String, nillable=False)

    @classmethod
    def create(cls, value):
        instance = cls()
        instance.value = value
        return instance

def _echo_handler():
    state = AttrDict(was_called=False)
    def _handler(request, input_):
        state.update(dict(
            was_called = True,
            request = request,
            input_ = input_,
            input_header = request.soap_header,
        ))
        return SoapboxResponse(EchoType.create(input_.value))
    return _handler, state

class InputHeader(xsd.ComplexType):
    InputVersion = xsd.Element(xsd.String)

class OutputHeader(xsd.ComplexType):
    OutputVersion = xsd.Element(xsd.String)

def _echo_service(handler=None, input_header=None, output_header=None):
    if handler is None:
        handler, handler_state = _echo_handler()

    EchoSchema = xsd.Schema(
        'http://soap.example/echo/types',
        elementFormDefault=xsd.ElementFormDefault.UNQUALIFIED,
        complexTypes=(EchoType, InputHeader, OutputHeader),
        elements={
            'echoRequest': xsd.Element(EchoType),
            'echoResponse': xsd.Element(EchoType),
        },
    )
    echo_method = xsd.Method(function=handler,
        soapAction='echo',
        input='echoRequest',
        inputPartName='input_',
        input_header=input_header,
        output='echoResponse',
        output_header=output_header,
        outputPartName='result',
        operationName='echoOperation',
    )
    return soap.Service(
        name='TestService',
        targetNamespace='http://soap.example/echo',
        location='http://soap.example/ws',
        schema=EchoSchema,
        version=soap.SOAPVersion.SOAP11,
        methods={
            'echo': echo_method,
        },
    )

def _faulty_handler():
    soap_error = SOAPError('some error', 'foobar', 'internal data error')
    return lambda request, input_: SoapboxResponse(soap_error)


class SoapDispatcherTest(PythonicTestCase):
    def test_can_dispatch_good_soap_message(self):
        handler, handler_state = _echo_handler()
        dispatcher = SOAPDispatcher(_echo_service(handler))
        soap_message = ('<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<value>foobar</value>'
        '</ns1:echoRequest>')
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SoapboxRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), request_message)

        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response, handler_state)
        assert_equals('foobar', handler_state.input_.value)

        response_document = etree.fromstring(response.message)
        response_xml = etree.tostring(response_document, pretty_print=True)
        expected_xml = (
            b'<ns0:Envelope xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/">\n'
            b'  <ns0:Body>\n'
            b'    <ns0:echoResponse xmlns:ns0="http://soap.example/echo/types">\n'
            b'      <value>foobar</value>\n'
            b'    </ns0:echoResponse>\n'
            b'  </ns0:Body>\n'
            b'</ns0:Envelope>\n'
        )
        assert_equals(expected_xml, response_xml)

    def test_can_validate_soap_message(self):
        handler, handler_state = _echo_handler()
        dispatcher = SOAPDispatcher(_echo_service(handler))
        soap_message = ('<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<invalid>foobar</invalid>'
            '</ns1:echoRequest>')
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SoapboxRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), request_message)

        response = dispatcher.dispatch(request)
        assert_false(handler_state.was_called)
        self.assert_is_soap_fault(response,
            partial_fault_string=u"Element 'invalid': This element is not expected. Expected is ( value ).")

    def test_can_reject_malformed_xml_soap_message(self):
        request = SoapboxRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), 'garbage')
        dispatcher = SOAPDispatcher(_echo_service())
        response = dispatcher.dispatch(request)
        assert_equals(500, response.status)
        assert_equals('text/xml', response.content_type)
        self.assert_is_soap_fault(response, partial_fault_string=u"Start tag expected, '<' not found")

    def test_can_reject_non_soap_xml_body(self):
        request = SoapboxRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), '<some>xml</some>')
        dispatcher = SOAPDispatcher(_echo_service())

        # previously this raised an AttributeError due to an unhandled exception
        response = dispatcher.dispatch(request)
        assert_equals(500, response.status)
        assert_equals('text/xml', response.content_type)
        self.assert_is_soap_fault(response, partial_fault_string=u'Missing SOAP body')

    def test_can_dispatch_requests_based_on_soap_body(self):
        handler, handler_state = _echo_handler()
        dispatcher = SOAPDispatcher(_echo_service(handler))
        soap_message = ('<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<value>foobar</value>'
        '</ns1:echoRequest>')
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SoapboxRequest(dict(SOAPACTION='""', REQUEST_METHOD='POST'), request_message)
        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response, handler_state)

    def test_can_use_soap_error_from_handler(self):
        faulty_handler = _faulty_handler()
        dispatcher = SOAPDispatcher(_echo_service(handler=faulty_handler))
        soap_message = ('<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<value>foobar</value>'
        '</ns1:echoRequest>')
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SoapboxRequest(dict(REQUEST_METHOD='POST'), request_message)

        response = dispatcher.dispatch(request)
        assert_equals('text/xml', response.content_type)
        assert_equals(500, response.status)
        self.assert_is_soap_fault(response,
            fault_code='foobar',
            partial_fault_string=u'internal data error'
        )

    def test_can_propagete_custom_input_header(self):
        handler, handler_state = _echo_handler()
        dispatcher = SOAPDispatcher(_echo_service(handler, input_header=InputHeader))
        soap_header = ('<tns:InputVersion>42</tns:InputVersion>')
        soap_message = ('<tns:echoRequest>'
            '<value>foobar</value>'
        '</tns:echoRequest>')
        request_message = self._wrap_with_soap_envelope(soap_message, header=soap_header)
        request = SoapboxRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), request_message)
        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response, handler_state)
        assert_not_none(handler_state.input_header)
        self.assertEqual('42', handler_state.input_header.InputVersion)

    def test_can_handle_empty_input_header(self):
        handler, handler_state = _echo_handler()
        dispatcher = SOAPDispatcher(_echo_service(handler, input_header=InputHeader))
        soap_message = ('<tns:echoRequest xmlns:tns="http://soap.example/echo/types">'
            '<value>foobar</value>'
        '</tns:echoRequest>')
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SoapboxRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), request_message)
        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response, handler_state)

    def test_can_propagete_custom_output_header(self):
        handler, handler_state = _echo_handler()
        def _handler(request, _input):
            resp = handler(request, _input)
            resp.soap_header = OutputHeader(OutputVersion = '42')
            return resp
        dispatcher = SOAPDispatcher(_echo_service(_handler, output_header=OutputHeader))
        soap_header = ('<tns:InputVersion>42</tns:InputVersion>')
        soap_message = ('<tns:echoRequest xmlns:tns="http://soap.example/echo/types">'
            '<value>foobar</value>'
        '</tns:echoRequest>')
        request_message = self._wrap_with_soap_envelope(soap_message, header=soap_header)
        request = SoapboxRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), request_message)
        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response, handler_state)
        assert_contains(b'<ns0:OutputVersion>42</ns0:OutputVersion>', response.message)

    def test_can_handle_empty_output_header(self):
        handler, handler_state = _echo_handler()
        dispatcher = SOAPDispatcher(_echo_service(handler, output_header=OutputHeader))
        soap_message = ('<tns:echoRequest xmlns:tns="http://soap.example/echo/types">'
            '<value>foobar</value>'
        '</tns:echoRequest>')
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SoapboxRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), request_message)
        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response, handler_state)

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

    def _wrap_with_soap_envelope(self, payload, header=''):
        if header:
            header = '<senv:Header>{header}</senv:Header>'.format(header=header)
        envelope = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<senv:Envelope xmlns:senv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://soap.example/echo/types">'
            '%(header)s'
            '<senv:Body>%(payload)s</senv:Body>'
            '</senv:Envelope>'
        ) % dict(payload=payload, header=header)
        return envelope.encode('utf-8')


class WsgiTest(PythonicTestCase):

    def test_wsgi(self):
        service = _echo_service()
        dispatcher = SOAPDispatcher(service)
        app = WsgiSoapApplication({'/service': dispatcher})
        class StartResponse():
            self.code = None
            self.headers = None
            def __call__(self, code, headers):
                self.code = code
                self.headers = headers
        start_response = StartResponse()
        soap_message = (b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<senv:Envelope xmlns:senv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://soap.example/echo/types">'
            b'<senv:Body>'
            b'<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            b'<value>foobar</value>'
            b'</ns1:echoRequest>'
            b'</senv:Body>'
            b'</senv:Envelope>')
        response_xml = b''.join(app({
            'SOAPACTION': 'echo',
            'PATH_INFO': '/service',
            'CONTENT_LENGTH': len(soap_message),
            'QUERY_STRING': '',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '7000',
            'REQUEST_METHOD': 'POST',
            'wsgi.url_scheme': 'http',
            'wsgi.input': io.BytesIO(soap_message),
        }, start_response))
        dict_headers = dict(start_response.headers)
        expected_xml = (
            b'<ns0:Envelope xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/">\n'
            b'  <ns0:Body>\n'
            b'    <ns0:echoResponse xmlns:ns0="http://soap.example/echo/types">\n'
            b'      <value>foobar</value>\n'
            b'    </ns0:echoResponse>\n'
            b'  </ns0:Body>\n'
            b'</ns0:Envelope>\n'
        )
        self.assertEqual(expected_xml, response_xml)
        self.assertEqual(WsgiSoapApplication.HTTP_200, start_response.code)
        self.assertEqual('text/xml', dict_headers['content-type'])




