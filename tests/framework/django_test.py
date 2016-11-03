from __future__ import absolute_import

import unittest
from collections import namedtuple
from datetime import datetime

from soapfish.django_ import django_dispatcher
from soapfish.testutil import echo_service, framework

try:
    import django
    from django.conf import settings
except (ImportError, SyntaxError):
    # XXX: SyntaxError caused by Django 1.8+ on Python 2.6
    django = None
else:
    settings.configure(
        ALLOWED_HOSTS=['testserver'],
        ROOT_URLCONF=None,
        DEBUG=True,
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        EMAIL_BACKEND='django.core.mail.backends.dummy.EmailBackend',
        LOGGING_CONFIG=None,
        USE_I18N=False,
        USE_TZ=True,
    )
    from django.conf.urls import url
    from django.test import Client

if not hasattr(unittest, 'skip'):
    # XXX: Skipping tests not supported in Python 2.6
    import unittest2 as unittest


urlconf = namedtuple('urlconf', 'urlpatterns')


@unittest.skipIf(django is None, 'Django is not installed.')
class DjangoDispatchTest(framework.DispatchTestMixin, unittest.TestCase):

    def setUp(self):  # noqa
        # XXX: Python 2.6 and unittest2 still call this method for skipped class.
        if django is None:
            self.skipTest('Django is not installed.')

        self.service = echo_service()
        settings.ROOT_URLCONF = urlconf(urlpatterns=(url(r'^ws/$', django_dispatcher(self.service)),))
        self.client = Client()

    def _prepare_extras(self, headers):
        extras = dict(('HTTP_' + k.replace('-', '_').upper(), v) for k, v in headers.items())
        extras.update(content_type=headers['content-type'])
        return extras

    def test_can_retrieve_wsdl(self):
        response = self.client.get('/ws/', {'wsdl': None})
        self.assertEquals(200, response.status_code)
        self.assertEquals('text/xml', response['Content-Type'])
        self.assertIn(b'<wsdl:definitions', response.content)

    def test_can_dispatch_simple_request(self):
        input_value = str(datetime.now())
        headers, body = self._soap_request(input_value)
        extras = self._prepare_extras(headers)
        response = self.client.post('/ws/', body, **extras)
        self.assertEquals(200, response.status_code)
        body = self._soap_response(response.content)
        self.assertEquals(input_value, body.value)
