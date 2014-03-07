# -*- coding: utf-8 -*-

from __future__ import absolute_import

import functools
import logging
from lxml import etree
import six

from . import core
from . import middlewares as mw
from . import soap
from .lib.attribute_dict import AttrDict
from .lib.result import ValidationResult
from .utils import uncapitalize

basestring = six.string_types

__all__ = ['SOAPDispatcher']

logger = logging.getLogger(__name__)


def call_method(request):
    response = request.method.function(request, request.soap_body)
    if not isinstance(response, core.SoapboxResponse):
        response = SoapboxResponse(response)
    return response


class SOAPDispatcher(object):

    def __init__(self, service, middlewares=None):
        self.service = service
        if middlewares is None:
            middlewares = []
        self.middlewares = middlewares

    def middleware(self, i=0):
        if i == len(self.middlewares):
            # at the end call the method
            return call_method
        return functools.partial(self.middlewares[i], next_call=self.middleware(i+1))

    def handle_request_for_wsdl(self, request):
        pass

    def _parse_soap_content(self, xml):
        SOAP = self.service.version
        try:
            envelope = SOAP.Envelope.parsexml(xml)
        except etree.XMLSyntaxError as e:
            return ValidationResult(False, errors=(e,))
        # Actually this is more a stopgap measure than a real fix. The real
        # fix is to change SOAP.Envelope/ComplexType so it raise some kind of
        # validation error. A missing SOAP body is not allowed by the SOAP
        # specs (according to my interpretation):
        # SOAP 1.1: http://schemas.xmlsoap.org/soap/envelope/
        # SOAP 1.2: http://www.w3.org/2003/05/soap-envelope/
        if envelope.Body is None:
            return ValidationResult(False, errors=['Missing SOAP body'])
        return ValidationResult(True, validated_document=envelope)

    def _find_handler_for_request(self, request, message):
        SOAP = self.service.version
        soap_action = SOAP.determine_soap_action(request)
        root_tag = None
        if not soap_action:
            root_tag = self._find_root_tag(message)
            logger.warning('Soap action not found in http headers, use root tag "%s".', root_tag)
        else:
            logger.info('Soap action found in http headers: %s', soap_action)
        # TODO: handle invalid xml
        for method in self.service.methods.values():
            if soap_action:
                if soap_action == method.soapAction:
                    return method
            elif root_tag == method.input:
                return method
        return None

    def _find_root_tag(self, message):
        body_document = etree.fromstring(message)
        # TODO: catch invalid xml
        root = body_document.getroottree().getroot()
        ns = root.nsmap[root.prefix]
        return root.tag[len('{%s}' % ns):]

    def _parse_input(self, method, message):
        input_parser = method.input
        if isinstance(method.input, basestring):
            element = self.service.schema.elements[method.input]
            input_parser = element._type

        schema = self.service.schema
        try:
            validate_input = input_parser.parsexml(message, schema=schema)
        except etree.XMLSyntaxError as e:
            return ValidationResult(False, errors=(e,))
        return ValidationResult(True, validated_document=validate_input)

    def _validate_response(self, return_object, tagname):
        return_object.xml(tagname, namespace=self.service.schema.targetNamespace,
                          elementFormDefault=self.service.schema.elementFormDefault,
                          schema=self.service.schema)  # Validation.

    def response(self, message, is_error=False):
        SOAP = self.service.version
        http_status_code = 200 if (not is_error) else 500
        return AttrDict(
            status=http_status_code,
            content_type=SOAP.CONTENT_TYPE,
            message=message,
        )

    def error_response(self, soap_code, errors):
        SOAP = self.service.version
        first_error = errors[0]
        error_text = str(first_error)
        fault_message = SOAP.get_error_response(SOAP.Code.CLIENT, error_text)
        return self.response(fault_message, is_error=True)

    def dispatch(self, request):
        if request.environ['REQUEST_METHOD'] != 'POST':
            return AttrDict(
                status=400,
                content_type='text/plain',
                message='bad request',
            )
        request.dispatcher = self
        SOAP = self.service.version
        message_validation = self._parse_soap_content(request.content)
        if not message_validation.value:
            return self.error_response(SOAP.Code.CLIENT, message_validation.errors)
        soap_envelope = message_validation.validated_document
        soap_request_message = soap_envelope.Body.content()

        handler = self._find_handler_for_request(request, soap_request_message)
        # if not handler -> client error
        #  response = SOAP.get_error_response(SOAP.Code.CLIENT, str(e))

        # TODO return soap fault if header is required but missing in the input
        if soap_envelope.Header is not None:
            if handler.input_header:
                request.soap_header = soap_envelope.Header.parse_as(handler.input_header)
            elif self.service.input_header:
                request.soap_header = soap_envelope.Header.parse_as(self.service.input_header)

        request.method = handler

        input_validation = self._parse_input(handler, soap_request_message)
        if not input_validation.value:
            return self.error_response(SOAP.Code.CLIENT, input_validation.errors)
        validated_input = input_validation.validated_document

        request.soap_body = validated_input

        # LATER: the dispatcher should be able to also catch arbitrary
        # exceptions from the handler. At the same time the caller should be
        # able to install custom hooks for these exceptions (e.g. custom
        # traceback logging) and we should support popular debugging middlewares
        # somehow.
        response = self.middleware()(request)

        SOAP = self.service.version

        if not isinstance(response, core.SoapboxResponse):
            response = core.SoapboxResponse(response)
        if isinstance(response.content, core.SOAPError):
            error = response.content
            error_response = SOAP.get_error_response(error.code, error.message, header=response.soap_header)
            return self.response(error_response, is_error=True)

        tagname = uncapitalize(response.content.__class__.__name__)
        #self._validate_response(response.content, tagname)
        # TODO: handle validation results

        if isinstance(request.method.output, basestring):
            tagname = request.method.output
        else:
            tagname = uncapitalize(response.content.__class__.__name__)

        response_xml = SOAP.Envelope.response(tagname, response.content, header=response.soap_header)

        return self.response(response_xml, is_error=False)


class WsgiSoapApplication(object):
    HTTP_500 = '500 Internal server error'
    HTTP_200 = '200 OK'
    HTTP_405 = '405 Method Not Allowed'

    def __init__(self, dispatchers):
        '''
        Args:
            dispatcher: mapping of url to dispatcher. ex: {'/service1': <class SOAPDispatcher>}
        '''
        self.dispatchers = dispatchers

    def __call__(self, req_env, start_response, wsgi_url=None):
        dispatcher = self.dispatchers[req_env['PATH_INFO']]
        content_length = int(req_env.get('CONTENT_LENGTH', 0))
        content = req_env['wsgi.input'].read(content_length)
        soap_request = core.SoapboxRequest(req_env, content)
        response = dispatcher.dispatch(soap_request)
        response_headers = [
            ("content-type", response['content_type']),
        ]
        start_response(self._get_http_status(response.status), response_headers)
        return [response.message]

    def _get_http_status(self, response_status):
        if response_status == 200:
            return self.HTTP_200
        elif response_status == 500:
            return self.HTTP_500
        elif response_status == 405:
            return self.HTTP_405
        else:
            # wsgi wants an http status of len >= 4
            # TODO do a better status code transformation
            return str(response_status) + ' '
