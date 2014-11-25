# -*- coding: utf-8 -*-
'''
SOAP protocol implementation, dispatchers and client stub.
'''

import httplib2
import logging
import os

from . import core
from . import settings, soap11, soap12
from . import namespaces as ns
from . import wsa
from .compat import basestring, urlparse
from .utils import uncapitalize

SOAP_HTTP_Transport = ns.wsdl_soap_http


logger = logging.getLogger('soapfish')


class SOAPVersion:
    SOAP12 = soap12
    SOAP11 = soap11

    @classmethod
    def get_version(cls, namespace):
        if namespace == cls.SOAP11.ENVELOPE or namespace == cls.SOAP11.BINDING:
            return cls.SOAP11
        elif  namespace == cls.SOAP12.ENVELOPE or namespace == cls.SOAP12.BINDING:
            return cls.SOAP11
        else:
            raise ValueError("SOAP version with namespace '%s' is not supported." % namespace)

    @classmethod
    def get_version_name(cls, namespace):
        version = cls.get_version(namespace)
        return version.__name__

    @classmethod
    def get_version_from_xml(cls, xml):
        namespaces = {'wsdl': ns.wsdl, 'soap12': ns.wsdl_soap12}
        if xml.xpath('wsdl:binding/soap12:binding', namespaces=namespaces):
            return cls.SOAP12
        else:
            return cls.SOAP11



class Service(object):
    '''
    Describes service aggregating information required for dispatching and
    WSDL generation.
    '''

    def __init__(self, targetNamespace, location, schema, methods,
                 version=SOAPVersion.SOAP11, name='Service',
                 input_header=None, output_header=None, use_wsa=False):
        '''
        :param targetNamespace: string
        :param location: string, endpoint url.
        :param schema: xsd.Schema instance.
        :param methods: list of xsd.Methods
        '''
        self.name = name
        self.targetNamespace = targetNamespace
        self.location = location
        self.schema = schema
        self.methods = methods
        self.version = version
        self.use_wsa = use_wsa
        if use_wsa and input_header is None:
            input_header = wsa.WSAsaHeader
        if use_wsa and output_header is None:
            output_header = wsa.WSAHeader
        self.input_header = input_header
        self.output_header= output_header

    def get_method(self, operationName):
        return filter(lambda m: m.operationName == operationName, self.methods)[0]


class Stub(object):
    '''
    Client stub. Handles only document style calls.
    '''
    SERVICE = None
    SCHEME = 'http'
    HOST = 'www.example.net'

    def __init__(self, username=None, password=None, service=None, location=None, base_url=None):
        self.username = username
        self.password = password
        self.service = service if service else self.SERVICE
        if location:
            self.location = location
        elif base_url:
            p = urlparse(base_url)
            self.location = self.service.location % {
                'scheme': p.scheme,
                'host': p.netloc,
            }
        else:
            self.location = self.service.location % {
                'scheme': self.SCHEME,
                'host': self.HOST,
            }

    def _handle_response(self, method, http_headers, content):
        SOAP = self.SERVICE.version
        envelope = SOAP.Envelope.parsexml(content)

        if envelope.Header and method and method.output_header:
            response_header = envelope.Header.parse_as(method.output_header)
        else:
            response_header = None

        if envelope.Body.Fault:
            code, message, actor = SOAP.parse_fault_message(envelope.Body.Fault)
            error = core.SOAPError(code=code, message=message, actor=actor)
            raise error

        if isinstance(method.output, basestring):
            element = self.SERVICE.schema.get_element_by_name(method.output)
            _type = element._type.__class__
        else:
            _type = method.output

        body = envelope.Body.parse_as(_type)
        return core.SOAPResponse(body, soap_header=response_header)

    def call(self, operationName, parameter, header=None):
        '''
        :raises: lxml.etree.XMLSyntaxError -- validation problems.
        '''
        SOAP = self.SERVICE.version
        method = self.SERVICE.get_method(operationName)

        if isinstance(method.input, basestring):
            tagname = method.input
        else:
            tagname = uncapitalize(parameter.__class__.__name__)

        disable_validation = not os.path.exists(settings.CA_CERTIFICATE_FILE)
        http = httplib2.Http(
            ca_certs=settings.CA_CERTIFICATE_FILE,
            disable_ssl_certificate_validation=disable_validation,
            timeout=settings.REQUEST_TIMEOUT,
        )
        if self.username:
            http.add_credentials(self.username, self.password)

        headers = SOAP.build_http_request_headers(method.soapAction)
        envelope = SOAP.Envelope.response(tagname, parameter, header=header)

        logger.info("Call %r on %r", operationName, self.location)
        logger.debug("Request Headers: %s", headers)
        logger.debug("Request Envelope: %s", envelope)
        headers, content = http.request(self.location, 'POST',
             body=envelope, headers=headers)
        logger.debug("Response Headers: %s", headers)
        logger.debug("Response Envelope: %s", content)

        return self._handle_response(method, headers, content)
