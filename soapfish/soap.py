# -*- coding: utf-8 -*-
'''
SOAP protocol implementation, dispatchers and client stub.
'''

import logging

import requests
import six

from . import core, namespaces as ns, soap11, soap12, wsa
from .utils import uncapitalize

SOAP_HTTP_Transport = ns.wsdl_soap_http


logger = logging.getLogger('soapfish')


class SOAPVersion:
    SOAP12 = soap12
    SOAP11 = soap11

    @classmethod
    def get_version(cls, namespace):
        if namespace == cls.SOAP11.ENVELOPE_NAMESPACE or namespace == cls.SOAP11.BINDING_NAMESPACE:
            return cls.SOAP11
        elif namespace == cls.SOAP12.ENVELOPE_NAMESPACE or namespace == cls.SOAP12.BINDING_NAMESPACE:
            return cls.SOAP12
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

    def __init__(self, targetNamespace, location, schemas, methods,
                 version=SOAPVersion.SOAP11, name='Service',
                 input_header=None, output_header=None, use_wsa=False):
        '''
        :param targetNamespace: string
        :param location: string, endpoint url.
        :param schemas: xsd.Schema instances.
        :param methods: list of xsd.Methods
        '''
        self.name = name
        self.targetNamespace = targetNamespace
        self.location = location
        self.schemas = schemas
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
        return tuple(filter(lambda m: m.operationName == operationName, self.methods))[0]

    def find_element_by_name(self, name):
        element = None
        for schema in self.schemas:
            element = schema.get_element_by_name(name)
            if element is not None:
                break
        return element

    def route(self, operationName):
        """Decorator to bind a Python function to service method."""
        method = self.get_method(operationName)

        def wrapper(func):
            method.function = func
            return func
        return wrapper


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
        else:
            if base_url:
                p = six.moves.urllib.parse.urlparse(base_url)
                parts = {'scheme': p.scheme, 'host': p.netloc}
            else:
                parts = {'scheme': self.SCHEME, 'host': self.HOST}
            self.location = self.service.location.format(**parts)

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

        if isinstance(method.output, six.string_types):
            element = self.SERVICE.find_element_by_name(method.output)
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

        if isinstance(method.input, six.string_types):
            tagname = method.input
        else:
            tagname = uncapitalize(parameter.__class__.__name__)

        auth = (self.username, self.password) if self.username else None
        data = SOAP.Envelope.response(tagname, parameter, header=header)
        headers = SOAP.build_http_request_headers(method.soapAction)

        logger.info("Call '%s' on '%s'", operationName, self.location)
        logger.debug('Request Headers: %s', headers)
        logger.debug('Request Envelope: %s', data)
        r = requests.post(self.location, auth=auth, headers=headers, data=data)
        logger.debug('Response Headers: %s', r.headers)
        logger.debug('Response Envelope: %s', r.content)
        return self._handle_response(method, r.headers, r.content)
