from __future__ import absolute_import

import six
from lxml import etree
from pythonic_testcase import (
    PythonicTestCase,
    assert_contains,
    assert_equals,
    assert_false,
    assert_length,
    assert_not_contains,
    assert_not_none,
    assert_raises,
    assert_true,
)

from soapfish import wsa, xsd
from soapfish.core import SOAPError, SOAPRequest, SOAPResponse
from soapfish.middlewares import ExceptionToSoapFault
from soapfish.soap_dispatch import SOAPDispatcher
from soapfish.testutil import (
    EchoInputHeader,
    EchoOutputHeader,
    echo_handler,
    echo_service,
)


class SOAPDispatcherTest(PythonicTestCase):
    def test_can_dispatch_good_soap_message(self):
        handler, handler_state = echo_handler()
        dispatcher = SOAPDispatcher(echo_service(handler))
        soap_message = (
            '<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<value>foobar</value>'
            '</ns1:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SOAPRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), request_message)

        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response, handler_state)
        assert_equals('foobar', handler_state.input_.value)

        response_document = etree.fromstring(response.http_content)
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
        handler, handler_state = echo_handler()
        dispatcher = SOAPDispatcher(echo_service(handler))
        soap_message = (
            '<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<invalid>foobar</invalid>'
            '</ns1:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SOAPRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), request_message)
        response = dispatcher.dispatch(request)
        assert_false(handler_state.was_called)
        self.assert_is_soap_fault(response, partial_fault_string=u"Element 'invalid': This element is not expected. "
                                  u'Expected is ( value ).')

    def test_can_reject_malformed_xml_soap_message(self):
        request = SOAPRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), 'garbage')
        dispatcher = SOAPDispatcher(echo_service())
        response = dispatcher.dispatch(request)
        assert_equals(500, response.http_status_code)
        assert_equals('text/xml', response.http_headers['Content-Type'])
        self.assert_is_soap_fault(response, partial_fault_string=u"Start tag expected, '<' not found")

    def test_can_include_imported_schemas_during_validation(self):
        # In case the SOAPDispatcher would not use imported schemas for
        # validation it would fail because the 'code' tag is only defined in
        # the imported schema
        handler, handler_state = echo_handler()
        service = echo_service(handler)

        class CodeType(xsd.String):
            pattern = r'[0-9]{5}'

        class Container(xsd.ComplexType):
            value = xsd.Element(CodeType)
        code_schema = xsd.Schema('http://soap.example/included',
                                 location='http://soap.example/included',
                                 elementFormDefault=xsd.ElementFormDefault.UNQUALIFIED,
                                 simpleTypes=[CodeType],
                                 complexTypes=[Container],
                                 elements={'foo': xsd.Element(Container)},
                                 )
        service.methods[0].input = 'foo'
        service.schemas[0].imports = [code_schema]
        # The setup is a bit simplistic because the <code> tag is not parsed
        # into a soapfish model element for the handler but this was enough
        # to trigger the bug
        dispatcher = SOAPDispatcher(service)
        wsgi_environ = dict(SOAPACTION='echo', REQUEST_METHOD='POST')
        soap_message = '<ns0:foo xmlns:ns0="http://soap.example/included"><value>12345</value></ns0:foo>'
        request = SOAPRequest(wsgi_environ, self._wrap_with_soap_envelope(soap_message))
        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response, handler_state)
        assert_equals('12345', handler_state.input_.value)

    def test_can_reject_non_soap_xml_body(self):
        request = SOAPRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), '<some>xml</some>')
        dispatcher = SOAPDispatcher(echo_service())

        # previously this raised an AttributeError due to an unhandled exception
        response = dispatcher.dispatch(request)
        assert_equals(500, response.http_status_code)
        assert_equals('text/xml', response.http_headers['Content-Type'])
        self.assert_is_soap_fault(response, partial_fault_string=u'Missing SOAP body')

    def test_can_reject_invalid_action(self):
        soap_message = (
            '<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<value>foobar</value>'
            '</ns1:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SOAPRequest(dict(SOAPACTION='invalid', REQUEST_METHOD='POST'), request_message)
        dispatcher = SOAPDispatcher(echo_service())
        response = dispatcher.dispatch(request)
        self.assert_is_soap_fault(response, partial_fault_string=u"Invalid soap action 'invalid'")

    def test_can_reject_invalid_root_tag(self):
        soap_message = ('<ns0:invalid xmlns:ns0="invalid"/>')
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SOAPRequest(dict(REQUEST_METHOD='POST'), request_message)
        dispatcher = SOAPDispatcher(echo_service())
        response = dispatcher.dispatch(request)
        self.assert_is_soap_fault(response, partial_fault_string='DocumentInvalid')

    def test_can_dispatch_requests_based_on_soap_body(self):
        handler, handler_state = echo_handler()
        dispatcher = SOAPDispatcher(echo_service(handler))
        soap_message = (
            '<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<value>foobar</value>'
            '</ns1:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SOAPRequest(dict(SOAPACTION='""', REQUEST_METHOD='POST'), request_message)
        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response, handler_state)

    def test_can_use_soap_error_from_handler(self):
        soap_error = SOAPError('code', 'internal data error', 'actor')

        def faulty_handler(request, input_):
            return SOAPResponse(soap_error)
        dispatcher = SOAPDispatcher(echo_service(handler=faulty_handler))
        soap_message = (
            '<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<value>foobar</value>'
            '</ns1:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SOAPRequest(dict(REQUEST_METHOD='POST'), request_message)

        response = dispatcher.dispatch(request)
        assert_equals('text/xml', response.http_headers['Content-Type'])
        assert_equals(500, response.http_status_code)
        self.assert_is_soap_fault(response, fault_code='code', partial_fault_string=u'internal data error')

    def test_can_handle_xsd_element_as_return_value_from_handler(self):
        def handler(request, input_):
            return input_
        dispatcher = SOAPDispatcher(echo_service(handler))
        soap_message = (
            '<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<value>hello</value>'
            '</ns1:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SOAPRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), request_message)

        response = dispatcher.dispatch(request)
        body_text = response.http_content
        if not isinstance(body_text, six.string_types):
            body_text = body_text.decode('utf-8')
        assert_contains('<value>hello</value>', body_text)

    def test_can_propagate_custom_input_header(self):
        handler, handler_state = echo_handler()
        dispatcher = SOAPDispatcher(echo_service(handler, input_header=EchoInputHeader))
        soap_header = ('<tns:InputVersion>42</tns:InputVersion>')
        soap_message = (
            '<tns:echoRequest>'
            '<value>foobar</value>'
            '</tns:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message, header=soap_header)
        request = SOAPRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), request_message)
        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response, handler_state)
        assert_not_none(handler_state.input_header)
        assert_equals('42', handler_state.input_header.InputVersion)

    def test_can_handle_empty_input_header(self):
        handler, handler_state = echo_handler()
        dispatcher = SOAPDispatcher(echo_service(handler, input_header=EchoInputHeader))
        soap_message = (
            '<tns:echoRequest xmlns:tns="http://soap.example/echo/types">'
            '<value>foobar</value>'
            '</tns:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SOAPRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), request_message)
        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response, handler_state)

    def test_can_validate_soap_header(self):
        handler, handler_state = echo_handler()
        dispatcher = SOAPDispatcher(echo_service(handler, input_header=EchoInputHeader))
        soap_header = ('<tns:invalid>42</tns:invalid>')
        soap_message = (
            '<tns:echoRequest>'
            '<value>foobar</value>'
            '</tns:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message, header=soap_header)
        request = SOAPRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), request_message)
        response = dispatcher.dispatch(request)
        self.assert_is_soap_fault(response, partial_fault_string='DocumentInvalid')

    def test_can_propagate_custom_output_header(self):
        handler, handler_state = echo_handler()

        def _handler(request, _input):
            resp = handler(request, _input)
            resp.soap_header = EchoOutputHeader(OutputVersion='42')
            return resp
        dispatcher = SOAPDispatcher(echo_service(_handler, output_header=EchoOutputHeader))
        soap_header = '<tns:InputVersion>42</tns:InputVersion>'
        soap_message = (
            '<tns:echoRequest xmlns:tns="http://soap.example/echo/types">'
            '<value>foobar</value>'
            '</tns:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message, header=soap_header)
        request = SOAPRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), request_message)
        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response, handler_state)
        assert_contains(b'<ns0:OutputVersion>42</ns0:OutputVersion>', response.http_content)

    def test_can_handle_empty_output_header(self):
        handler, handler_state = echo_handler()
        dispatcher = SOAPDispatcher(echo_service(handler, output_header=EchoOutputHeader))
        soap_message = (
            '<tns:echoRequest xmlns:tns="http://soap.example/echo/types">'
            '<value>foobar</value>'
            '</tns:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SOAPRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), request_message)
        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response, handler_state)

    def test_return_soap_fault_on_exception(self):
        def handler(request, _input):
            raise Exception('unexpected exception')
        service = echo_service(handler)
        dispatcher = SOAPDispatcher(service, [ExceptionToSoapFault()])
        soap_message = (
            '<tns:echoRequest xmlns:tns="http://soap.example/echo/types">'
            '<value>foobar</value>'
            '</tns:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SOAPRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'), request_message)
        response = dispatcher.dispatch(request)
        self.assert_is_soap_fault(response, fault_code=service.version.Code.SERVER,
                                  partial_fault_string='unexpected exception')
        assert_equals('text/xml', response.http_headers['Content-Type'])
        assert_equals(500, response.http_status_code)

    def test_can_validate_wsa_header(self):
        dispatcher = SOAPDispatcher(echo_service())
        header = wsa.Header.parsexml(
            '<Header><Action xmlns="http://www.w3.org/2005/08/addressing">/Action</Action></Header>'
        )
        dispatcher._validate_header(header)

    def test_can_detect_invalid_wsa_header(self):
        dispatcher = SOAPDispatcher(echo_service())
        header = wsa.Header.parsexml(
            '<Header><Invalid xmlns="http://www.w3.org/2005/08/addressing">/Action</Invalid></Header>'
        )
        assert_raises(etree.DocumentInvalid, lambda: dispatcher._validate_header(header))

    def test_evaluate_service_location(self):
        handler, _ = echo_handler()
        service = echo_service(handler)
        service.location = '${scheme}://${host}/ws'
        dispatcher = SOAPDispatcher(service)
        request = SOAPRequest(dict(REQUEST_METHOD='GET', QUERY_STRING='wsdl',
                                   HTTP_HOST='soap.example'), '')
        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response)
        assert_not_contains('${scheme}', response.http_content.decode())
        assert_not_contains('${host}', response.http_content.decode())

    def test_service_bind_function(self):
        handler, handler_state = echo_handler()
        service = echo_service(handler)

        @service.route('echoOperation')
        def echo_func(request, input_):
            handler_state.new_func_was_called = True
            return handler(request, input_)

        dispatcher = SOAPDispatcher(service)
        soap_message = (
            '<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<value>foobar</value>'
            '</ns1:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SOAPRequest(dict(SOAPACTION='echo', REQUEST_METHOD='POST'),
                              request_message)
        response = dispatcher.dispatch(request)

        assert_true(handler_state.new_func_was_called)
        self.assert_is_successful_response(response, handler_state)

    # --- custom assertions ---------------------------------------------------

    def assert_is_successful_response(self, response, handler_state=None):
        assert_equals(200, response.http_status_code)
        assert_equals('text/xml', response.http_headers['Content-Type'])
        if handler_state:
            assert_true(handler_state.was_called)

    def assert_is_soap_fault(self, response, fault_code=None, partial_fault_string=None):
        assert_equals(500, response.http_status_code)
        assert_equals('text/xml', response.http_headers['Content-Type'])

        fault_document = etree.fromstring(response.http_content)
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
        envelope = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<senv:Envelope xmlns:senv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://soap.example/echo/types">'
            '%(header)s'
            '<senv:Body>%(payload)s</senv:Body>'
            '</senv:Envelope>'
        ) % dict(payload=payload, header=header)
        return envelope.encode('utf-8')
