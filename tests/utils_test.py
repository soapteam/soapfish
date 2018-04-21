from __future__ import absolute_import

from datetime import timedelta

from pythonic_testcase import PythonicTestCase, assert_equals, assert_dict_contains, \
                            assert_false, assert_contains

from soapfish.utils import timezone_offset_to_string, get_requests_ssl_context
from soapfish import soap
import os
try:
    from test.test_support import EnvironmentVarGuard
except:
    from test.support import EnvironmentVarGuard

class FormatOffsetTest(PythonicTestCase):
    def test_can_format_positive_offsets(self):
        assert_equals('+00:00', timezone_offset_to_string(timedelta(0)))
        assert_equals('+04:27', timezone_offset_to_string(timedelta(hours=4, minutes=27)))
        assert_equals('+14:00', timezone_offset_to_string(timedelta(hours=14)))

    def test_can_format_negative_offsets(self):
        assert_equals('-00:30', timezone_offset_to_string(timedelta(minutes=-30)))
        assert_equals('-01:30', timezone_offset_to_string(timedelta(minutes=-90)))
        assert_equals('-14:00', timezone_offset_to_string(timedelta(hours=-14)))


class SSLExtraContextsetTest(PythonicTestCase):

    def test_verify_false(self):
        class NoSSLCheckStub(soap.Stub):
            SERVICE = None
            SCHEME = 'https'
            HOST = 'example.com'        
            REQUESTS_CA_CHECK=False

            def __init__(*args, **kwargs):
                pass
        
        context = get_requests_ssl_context(NoSSLCheckStub())
        assert_contains('verify', context )
        assert_false(context['verify'])

    def test_environment_verify_false(self):
        context = {}
        env = EnvironmentVarGuard()
        env.set('REQUESTS_CA_CHECK', 'False')
        with env:
            context = get_requests_ssl_context()
        assert_contains('verify', context )
        assert_false(context['verify'])

    def test_provide_CA_Certs(self):

        class MyServiceStub(soap.Stub):
            SERVICE = None
            SCHEME = 'https'
            HOST = 'example.com'
            REQUESTS_CA_PATH='/path/to/ca.crt'
            REQUESTS_CERT_PATH='/path/to/certificate.crt'
            REQUESTS_KEY_PATH='/path/to/key.pem'

            def __init__(*args, **kwargs):
                pass


        context = get_requests_ssl_context(MyServiceStub())
        assert_dict_contains( {'verify': '/path/to/ca.crt',
                                  'cert': ('/path/to/certificate.crt', 
                                           '/path/to/key.pem')
                              }, context)


    def test_environment_provide_CA_Certs(self):
        context={}
        env = EnvironmentVarGuard()
        env.set('REQUESTS_CA_PATH', '/path/to/ca.crt')
        env.set('REQUESTS_CERT_PATH', '/path/to/certificate.crt')
        env.set('REQUESTS_KEY_PATH', '/path/to/key.pem')
        with env:
           context = get_requests_ssl_context()
        assert_dict_contains( {'verify': '/path/to/ca.crt',
                                  'cert': ('/path/to/certificate.crt', 
                                           '/path/to/key.pem')
                              }, context)


    def test_provide_Cert_PEM(self):
        class MyServiceStub(soap.Stub):
            SERVICE = None
            SCHEME = 'https'
            HOST = 'example.com'
            REQUESTS_CERT_PATH='/path/to/certificate.pem'

            def __init__(*args, **kwargs):
                pass

        context = get_requests_ssl_context(MyServiceStub())
        assert_dict_contains({'cert': '/path/to/certificate.pem' }, context)

    def test_environment_provide_Cert_PEM(self):
        conext={}
        env = EnvironmentVarGuard()
        env.set('REQUESTS_CERT_PATH', '/path/to/certificate.pem')
        with env:
            context = get_requests_ssl_context()
        assert_dict_contains({'cert': '/path/to/certificate.pem' }, context)

