import unittest

from lxml import etree

from soapfish import wsa, xsd
from soapfish.core import SOAPError, SOAPRequest, SOAPResponse
from soapfish.middlewares import ExceptionToSoapFault
from soapfish.soap_dispatch import SOAPDispatcher
from soapfish.testutil import EchoInputHeader, EchoOutputHeader, echo_handler, echo_service


class SOAPDispatcherTest(unittest.TestCase):
    def test_can_dispatch_good_soap_message(self):
        handler, handler_state = echo_handler()
        dispatcher = SOAPDispatcher(echo_service(handler))
        soap_message = (
            '<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<value>foobar</value>'
            '</ns1:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SOAPRequest({'SOAPACTION': 'echo', 'REQUEST_METHOD': 'POST'}, request_message)

        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response, handler_state)
        self.assertEqual('foobar', handler_state.input_.value)

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
        self.assertEqual(expected_xml, response_xml)

    def test_can_validate_soap_message(self):
        handler, handler_state = echo_handler()
        dispatcher = SOAPDispatcher(echo_service(handler))
        soap_message = (
            '<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<invalid>foobar</invalid>'
            '</ns1:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SOAPRequest({'SOAPACTION': 'echo', 'REQUEST_METHOD': 'POST'}, request_message)
        response = dispatcher.dispatch(request)
        self.assertFalse(handler_state.was_called)
        self.assert_is_soap_fault(response, partial_fault_string="Element 'invalid': This element is not expected. "
                                  'Expected is ( value ).')

    def test_can_reject_malformed_xml_soap_message(self):
        request = SOAPRequest({'SOAPACTION': 'echo', 'REQUEST_METHOD': 'POST'}, 'garbage')
        dispatcher = SOAPDispatcher(echo_service())
        response = dispatcher.dispatch(request)
        self.assertEqual(500, response.http_status_code)
        self.assertEqual('text/xml', response.http_headers['Content-Type'])
        self.assert_is_soap_fault(response, partial_fault_string="Start tag expected, '<' not found")

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
        wsgi_environ = {'SOAPACTION': 'echo', 'REQUEST_METHOD': 'POST'}
        soap_message = '<ns0:foo xmlns:ns0="http://soap.example/included"><value>12345</value></ns0:foo>'
        request = SOAPRequest(wsgi_environ, self._wrap_with_soap_envelope(soap_message))
        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response, handler_state)
        self.assertEqual('12345', handler_state.input_.value)

    def test_can_reject_non_soap_xml_body(self):
        request = SOAPRequest({'SOAPACTION': 'echo', 'REQUEST_METHOD': 'POST'}, '<some>xml</some>')
        dispatcher = SOAPDispatcher(echo_service())

        # previously this raised an AttributeError due to an unhandled exception
        response = dispatcher.dispatch(request)
        self.assertEqual(500, response.http_status_code)
        self.assertEqual('text/xml', response.http_headers['Content-Type'])
        self.assert_is_soap_fault(response, partial_fault_string='Missing SOAP body')

    def test_can_reject_invalid_action(self):
        soap_message = (
            '<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            '<value>foobar</value>'
            '</ns1:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SOAPRequest({'SOAPACTION': 'invalid', 'REQUEST_METHOD': 'POST'}, request_message)
        dispatcher = SOAPDispatcher(echo_service())
        response = dispatcher.dispatch(request)
        self.assert_is_soap_fault(response, partial_fault_string='Invalid SOAP action: invalid')

    def test_can_reject_invalid_root_tag(self):
        soap_message = ('<ns0:invalid xmlns:ns0="invalid"/>')
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SOAPRequest({'REQUEST_METHOD': 'POST'}, request_message)
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
        request = SOAPRequest({'SOAPACTION': '""', 'REQUEST_METHOD': 'POST'}, request_message)
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
        request = SOAPRequest({'REQUEST_METHOD': 'POST'}, request_message)

        response = dispatcher.dispatch(request)
        self.assertEqual('text/xml', response.http_headers['Content-Type'])
        self.assertEqual(500, response.http_status_code)
        self.assert_is_soap_fault(response, fault_code='code', partial_fault_string='internal data error')

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
        request = SOAPRequest({'SOAPACTION': 'echo', 'REQUEST_METHOD': 'POST'}, request_message)

        response = dispatcher.dispatch(request)
        body_text = response.http_content
        if not isinstance(body_text, str):
            body_text = body_text.decode()
        self.assertIn('<value>hello</value>', body_text)

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
        request = SOAPRequest({'SOAPACTION': 'echo', 'REQUEST_METHOD': 'POST'}, request_message)
        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response, handler_state)
        self.assertIsNotNone(handler_state.input_header)
        self.assertEqual('42', handler_state.input_header.InputVersion)

    def test_can_handle_empty_input_header(self):
        handler, handler_state = echo_handler()
        dispatcher = SOAPDispatcher(echo_service(handler, input_header=EchoInputHeader))
        soap_message = (
            '<tns:echoRequest xmlns:tns="http://soap.example/echo/types">'
            '<value>foobar</value>'
            '</tns:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SOAPRequest({'SOAPACTION': 'echo', 'REQUEST_METHOD': 'POST'}, request_message)
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
        request = SOAPRequest({'SOAPACTION': 'echo', 'REQUEST_METHOD': 'POST'}, request_message)
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
        request = SOAPRequest({'SOAPACTION': 'echo', 'REQUEST_METHOD': 'POST'}, request_message)
        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response, handler_state)
        self.assertIn(b'<ns0:OutputVersion>42</ns0:OutputVersion>', response.http_content)

    def test_can_handle_empty_output_header(self):
        handler, handler_state = echo_handler()
        dispatcher = SOAPDispatcher(echo_service(handler, output_header=EchoOutputHeader))
        soap_message = (
            '<tns:echoRequest xmlns:tns="http://soap.example/echo/types">'
            '<value>foobar</value>'
            '</tns:echoRequest>'
        )
        request_message = self._wrap_with_soap_envelope(soap_message)
        request = SOAPRequest({'SOAPACTION': 'echo', 'REQUEST_METHOD': 'POST'}, request_message)
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
        request = SOAPRequest({'SOAPACTION': 'echo', 'REQUEST_METHOD': 'POST'}, request_message)
        response = dispatcher.dispatch(request)
        self.assert_is_soap_fault(response, fault_code=service.version.Code.SERVER,
                                  partial_fault_string='unexpected exception')
        self.assertEqual('text/xml', response.http_headers['Content-Type'])
        self.assertEqual(500, response.http_status_code)

    def test_can_validate_wsa_header(self):
        dispatcher = SOAPDispatcher(echo_service())
        header = wsa.Header.parsexml(
            '<Header><Action xmlns="http://www.w3.org/2005/08/addressing">/Action</Action></Header>',
        )
        dispatcher._validate_header(header)

    def test_can_detect_invalid_wsa_header(self):
        dispatcher = SOAPDispatcher(echo_service())
        header = wsa.Header.parsexml(
            '<Header><Invalid xmlns="http://www.w3.org/2005/08/addressing">/Action</Invalid></Header>',
        )
        with self.assertRaises(etree.DocumentInvalid):
            dispatcher._validate_header(header)

    def test_evaluate_service_location(self):
        handler, _ = echo_handler()
        service = echo_service(handler)
        service.location = '${scheme}://${host}/ws'
        dispatcher = SOAPDispatcher(service)
        request = SOAPRequest({'REQUEST_METHOD': 'GET', 'QUERY_STRING': 'wsdl', 'HTTP_HOST': 'soap.example'}, '')
        response = dispatcher.dispatch(request)
        self.assert_is_successful_response(response)
        self.assertNotIn('${scheme}', response.http_content.decode())
        self.assertNotIn('${host}', response.http_content.decode())

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
        request = SOAPRequest({'SOAPACTION': 'echo', 'REQUEST_METHOD': 'POST'}, request_message)
        response = dispatcher.dispatch(request)

        self.assertTrue(handler_state.new_func_was_called)
        self.assert_is_successful_response(response, handler_state)

    def test_hook_soap_request(self):
        message = (
            '<tns:echoRequest xmlns:tns="http://soap.example/echo/types">'
            '<value>Cast a hook to catch a soapfish.</value>'
            '</tns:echoRequest>'
        )
        request = SOAPRequest(
            {'REQUEST_METHOD': 'POST', 'SOAPACTION': 'echo'},
            self._wrap_with_soap_envelope(message),
        )

        def hook(dispatcher, request):
            request.http_content = request.http_content.replace(b'catch', b'snare')
            return request

        dispatcher = SOAPDispatcher(echo_service(), hooks={'soap-request': hook})
        response = dispatcher.dispatch(request)
        self.assertIn(b'Cast a hook to snare a soapfish.', response.http_content)

    def test_hook_soap_response(self):
        message = (
            '<tns:echoRequest xmlns:tns="http://soap.example/echo/types">'
            '<value>Cast a hook to catch a soapfish.</value>'
            '</tns:echoRequest>'
        )
        request = SOAPRequest(
            {'REQUEST_METHOD': 'POST', 'SOAPACTION': 'echo'},
            self._wrap_with_soap_envelope(message),
        )

        def hook(dispatcher, request, response):
            response.http_status_code = 999
            return response

        dispatcher = SOAPDispatcher(echo_service(), hooks={'soap-response': hook})
        response = dispatcher.dispatch(request)
        self.assertEqual(response.http_status_code, 999)

    # --- custom assertions ---------------------------------------------------

    def assert_is_successful_response(self, response, handler_state=None):
        self.assertEqual(200, response.http_status_code)
        self.assertEqual('text/xml', response.http_headers['Content-Type'])
        if handler_state:
            self.assertTrue(handler_state.was_called)

    def assert_is_soap_fault(self, response, fault_code=None, partial_fault_string=None):
        self.assertEqual(500, response.http_status_code)
        self.assertEqual('text/xml', response.http_headers['Content-Type'])

        fault_document = etree.fromstring(response.http_content)
        soap_envelope = fault_document.getroottree()
        namespaces = {'s': 'http://schemas.xmlsoap.org/soap/envelope/'}
        fault_nodes = soap_envelope.xpath('/s:Envelope/s:Body/s:Fault', namespaces=namespaces)
        self.assertEqual(len(fault_nodes), 1, msg='expected exactly one SOAP fault')
        children = list(fault_nodes[0])
        self.assertEqual(len(children), 2)

        xml_fault_code, fault_string = children
        if fault_code is None:
            fault_code = 'Client'
        self.assertEqual(fault_code, xml_fault_code.text)
        if partial_fault_string:
            self.assertIn(partial_fault_string, fault_string.text)

    # --- internal helpers ----------------------------------------------------

    def _wrap_with_soap_envelope(self, payload, header=''):
        if header:
            header = f'<senv:Header>{header}</senv:Header>'
        envelope = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<senv:Envelope xmlns:senv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://soap.example/echo/types">'
            '%(header)s'
            '<senv:Body>%(payload)s</senv:Body>'
            '</senv:Envelope>'
        ) % {'payload': payload, 'header': header}
        return envelope.encode()
