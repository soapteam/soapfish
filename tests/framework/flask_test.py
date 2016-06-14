from __future__ import absolute_import

import unittest
from datetime import datetime

from pythonic_testcase import *  # noqa

from soapfish.flask_ import flask_dispatcher
from soapfish.testutil import echo_service, framework

try:
    import flask
except ImportError:
    flask = None


@unittest.skipIf(flask is None, 'Flask is not installed.')
class FlaskDispatchTest(framework.DispatchTestMixin, PythonicTestCase):

    def setUp(self):  # noqa
        self.service = echo_service()
        app = flask.Flask(__name__)
        app.add_url_rule('/ws/', 'ws', flask_dispatcher(self.service), methods=['GET', 'POST'])
        self.client = app.test_client()

    def test_can_retrieve_wsdl(self):
        response = self.client.get('/ws/', query_string='wsdl')
        assert_equals(200, response.status_code)
        assert_equals('text/xml', response.headers['Content-Type'])
        assert_contains(b'<wsdl:definitions', response.data)

    def test_can_dispatch_simple_request(self):
        input_value = str(datetime.now())
        headers, body = self._soap_request(input_value)
        response = self.client.post('/ws/', data=body, headers=headers)
        assert_equals(200, response.status_code)
        body = self._soap_response(response.data)
        assert_equals(input_value, body.value)
