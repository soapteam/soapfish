import collections
import unittest
from datetime import datetime

from soapfish.django_ import django_dispatcher
from soapfish.testutil import echo_service, framework

try:
    import django
    from django.conf import settings
except ImportError:
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

urlconf = collections.namedtuple('urlconf', 'urlpatterns')


@unittest.skipIf(django is None, 'Django is not installed.')
class DjangoDispatchTest(framework.DispatchTestMixin, unittest.TestCase):

    def setUp(self):  # noqa
        self.service = echo_service()
        settings.ROOT_URLCONF = urlconf(urlpatterns=(url(r'^ws/$', django_dispatcher(self.service)),))
        self.client = Client()

    def _prepare_extras(self, headers):
        extras = {'HTTP_' + k.replace('-', '_').upper(): v for k, v in headers.items()}
        extras['content_type'] = headers['Content-Type']
        return extras

    def test_can_retrieve_wsdl(self):
        response = self.client.get('/ws/', {'wsdl': ''})
        self.assertEqual(200, response.status_code)
        self.assertEqual('text/xml', response['Content-Type'])
        self.assertIn(b'<wsdl:definitions', response.content)

    def test_can_dispatch_simple_request(self):
        input_value = str(datetime.now())
        headers, body = self._soap_request(input_value)
        extras = self._prepare_extras(headers)
        response = self.client.post('/ws/', body, **extras)
        self.assertEqual(200, response.status_code)
        body = self._soap_response(response.content)
        self.assertEqual(input_value, body.value)
