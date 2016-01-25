# encoding: utf-8

from __future__ import absolute_import

from datetime import datetime as DateTime

from pythonic_testcase import *
from soapfish.flask_ import flask_dispatcher
from soapfish.testutil import echo_service


class FlaskDispatchTest(PythonicTestCase):
    def setUp(self):
        try:
            from flask import Flask
        except ImportError:
            raise self.skipTest('flask not installed')

        super(FlaskDispatchTest, self).setUp()
        self.service = echo_service()

        app = Flask(__name__)
        app.add_url_rule('/ws/', 'ws', flask_dispatcher(self.service),
                         methods=['GET', 'POST'])

        self.client = app.test_client()

    def test_can_retrieve_wsdl_via_flask(self):
        response = self.client.get('/ws/', query_string='wsdl')
        assert_equals(200, response.status_code)
        assert_equals('text/xml', response.headers['Content-Type'])
        assert_contains('<wsdl:definitions', response.data.decode('utf-8'))

    def test_can_dispatch_simple_request_through_flask(self):
        input_value = str(DateTime.now())
        headers, body = self._soap_request(input_value)
        response = self.client.post('/ws/', data=body, headers=headers)
        assert_equals(200, response.status_code)
        body = self._parse_soap_response(response.data)
        assert_equals(input_value, body.value)

    # --- internal helpers ----------------------------------------------------
    def _soap_request(self, input_value):
        SOAP = self.service.version
        method = self.service.get_method('echoOperation')

        headers = SOAP.build_http_request_headers(method.soapAction)
        tagname = method.input
        EchoType = self.service.schema.get_element_by_name('echoRequest')._type
        echo = EchoType.create(input_value)
        request_body = SOAP.Envelope.response(tagname, echo)
        return headers, request_body

    def _parse_soap_response(self, response_body):
        SOAP = self.service.version
        method = self.service.get_method('echoOperation')

        envelope = SOAP.Envelope.parsexml(response_body)
        assert_none(envelope.Body.Fault)
        output_element = self.service.schema.get_element_by_name(method.output)
        output_ = output_element._type.__class__
        return envelope.Body.parse_as(output_)
