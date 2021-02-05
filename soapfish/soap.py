"""SOAP protocol implementation, dispatchers and client stub."""

import logging
import string

import httpx

from . import core, namespaces as ns, soap11, soap12, wsa
from .utils import uncapitalize

SOAP_HTTP_Transport = ns.wsdl_soap_http

logger = logging.getLogger('soapfish')


class SOAPVersion:
    SOAP11 = soap11
    SOAP12 = soap12

    @classmethod
    def get_version(cls, namespace):
        if namespace == cls.SOAP11.ENVELOPE_NAMESPACE or namespace == cls.SOAP11.BINDING_NAMESPACE:
            return cls.SOAP11
        elif namespace == cls.SOAP12.ENVELOPE_NAMESPACE or namespace == cls.SOAP12.BINDING_NAMESPACE:
            return cls.SOAP12
        else:
            raise ValueError(f"SOAP version with namespace '{namespace}' is not supported.")

    @classmethod
    def get_version_name(cls, namespace):
        return cls.get_version(namespace).__name__

    @classmethod
    def get_version_from_xml(cls, xml):
        namespaces = {'wsdl': ns.wsdl, 'soap12': ns.wsdl_soap12}
        return cls.SOAP12 if xml.xpath('wsdl:binding/soap12:binding', namespaces=namespaces) else cls.SOAP11


class Service:
    """Describe service aggregating information required for dispatching and WSDL generation."""

    def __init__(self, targetNamespace, location, schemas, methods, version=SOAPVersion.SOAP11, name='Service',
                 input_header=None, output_header=None, use_wsa=False):
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
        self.output_header = output_header

    def get_method(self, operationName):
        return next(m for m in self.methods if m.operationName == operationName)

    def find_element_by_name(self, name):
        element = None
        for schema in self.schemas:
            element = schema.get_element_by_name(name)
            if element is not None:
                break
        return element

    def route(self, operationName):
        """Return a decorator that binds a Python function to service method."""
        method = self.get_method(operationName)

        def wrapper(func):
            method.function = func
            return func

        return wrapper


class Stub:
    """Client stub. Handles only document style calls."""

    SERVICE = None
    SCHEME = 'http'
    HOST = 'www.example.net'

    def __init__(self, username=None, password=None, service=None, location=None):
        self.username = username
        self.password = password
        self.service = service if service else self.SERVICE

        context = {'scheme': self.SCHEME, 'host': self.HOST}
        if location is None:
            location = lambda template, context: string.Template(template).safe_substitute(**context)

        if callable(location):
            self.location = location(self.service.location, context)
        elif isinstance(location, str):
            self.location = location
        else:
            raise TypeError('Expected string or callable for location.')

    def _handle_response(self, method, http_headers, content):
        soap = self.service.version
        envelope = soap.Envelope.parsexml(content)

        if envelope.Header and method and method.output_header:
            response_header = envelope.Header.parse_as(method.output_header)
        else:
            response_header = None

        if envelope.Body.Fault:
            code, message, actor = soap.parse_fault_message(envelope.Body.Fault)
            error = core.SOAPError(code=code, message=message, actor=actor)
            raise error

        if isinstance(method.output, str):
            _type = self.service.find_element_by_name(method.output)._type.__class__
        else:
            _type = method.output

        body = envelope.Body.parse_as(_type)
        return core.SOAPResponse(body, soap_header=response_header)

    def call(self, operationName, parameter, header=None):
        soap = self.service.version
        method = self.service.get_method(operationName)
        tagname = method.input if isinstance(method.input, str) else uncapitalize(parameter.__class__.__name__)

        auth = (self.username, self.password) if self.username else None
        data = soap.Envelope.response(tagname, parameter, header=header)
        headers = soap.build_http_request_headers(method.soapAction)

        logger.info("Call '%s' on '%s'", operationName, self.location)
        logger.debug('Request Headers: %s', headers)
        logger.debug('Request Envelope: %s', data)
        r = httpx.post(self.location, auth=auth, headers=headers, data=data)
        logger.debug('Response Headers: %s', r.headers)
        logger.debug('Response Envelope: %s', r.content)
        return self._handle_response(method, r.headers, r.content)
