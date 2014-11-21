# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from io import BytesIO

from soapfish.lib.pythonic_testcase import *
from soapfish.soap_dispatch import SOAPDispatcher, WsgiSoapApplication
from soapfish.testutil import echo_service


class WsgiTest(PythonicTestCase):
    def test_can_dispatch_soap_request_with_plain_wsgi(self):
        service = echo_service()
        dispatcher = SOAPDispatcher(service)
        app = WsgiSoapApplication(dispatcher)
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
            'wsgi.input': BytesIO(soap_message),
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
        assert_equals(expected_xml, response_xml)
        assert_equals(WsgiSoapApplication.HTTP_200, start_response.code)
        assert_equals('text/xml', dict_headers['Content-Type'])

