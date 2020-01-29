import io
import unittest

from soapfish.soap_dispatch import SOAPDispatcher, WsgiSoapApplication
from soapfish.testutil import echo_service


class WsgiSoapApplicationTest(unittest.TestCase):
    def test_can_dispatch_soap_request_with_plain_wsgi(self):
        dispatcher = SOAPDispatcher(echo_service())
        app = WsgiSoapApplication(dispatcher)
        start_response = self._response_mock()
        soap_message = (
            b'<?xml version="1.0" encoding="utf-8"?>'
            b'<senv:Envelope xmlns:senv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://soap.example/echo/types">'
            b'<senv:Body>'
            b'<ns1:echoRequest xmlns:ns1="http://soap.example/echo/types">'
            b'<value>foobar</value>'
            b'</ns1:echoRequest>'
            b'</senv:Body>'
            b'</senv:Envelope>'
        )
        response = app(self._wsgi_env(soap_message), start_response)
        self.assertEqual('200 OK', start_response.code)
        self.assertEqual('text/xml', dict(start_response.headers)['Content-Type'])
        expected_xml = (
            b'<ns0:Envelope xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/">'
            b'<ns0:Body>'
            b'<ns0:echoResponse xmlns:ns0="http://soap.example/echo/types">'
            b'<value>foobar</value>'
            b'</ns0:echoResponse>'
            b'</ns0:Body>'
            b'</ns0:Envelope>'
        )
        self.assertEqual(expected_xml, b''.join(response))

    def _response_mock(self):
        class StartResponse():
            self.code = None
            self.headers = None

            def __call__(self, code, headers):
                self.code = code
                self.headers = headers
        return StartResponse()

    def _wsgi_env(self, soap_xml):
        return {
            'SOAPACTION': 'echo',
            'PATH_INFO': '/service',
            'CONTENT_LENGTH': len(soap_xml),
            'QUERY_STRING': '',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '7000',
            'REQUEST_METHOD': 'POST',
            'wsgi.url_scheme': 'http',
            'wsgi.input': io.BytesIO(soap_xml),
        }
