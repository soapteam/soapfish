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

    def _find_handler_for_request(self, request, body_document):
        SOAP = self.service.version
        soap_action = SOAP.determine_soap_action(request)
        root_tag = None
        if not soap_action:
            root_tag = self._find_root_tag(body_document)
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
        if soap_action is not None:
            raise core.SOAPError(SOAP.Code.CLIENT, "Invalid soap action '%s'" % soap_action)
        else:
            raise core.SOAPError(SOAP.Code.CLIENT, "Missing soap action and invalid root tag '%s'" % root_tag)

    def _find_root_tag(self, body_document):
        root = body_document
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
        except (etree.XMLSyntaxError, etree.DocumentInvalid) as e:
            return ValidationResult(False, errors=(e,))
        return ValidationResult(True, validated_document=validate_input)

    def _validate_response(self, return_object, tagname):
        return_object.xml(tagname, namespace=self.service.schema.targetNamespace,
                          elementFormDefault=self.service.schema.elementFormDefault,
                          schema=self.service.schema)  # Validation.

    def dispatch(self, request):
        if request.environ['REQUEST_METHOD'] != 'POST':
            return core.SoapboxResponse('bad request', http_status_code=400,
                http_content='bad_request', http_headers={'CONTENT_TYPE': 'text/plain'})

        request.dispatcher = self
        SOAP = self.service.version
        try:
            message_validation = self._parse_soap_content(request.content)
            if not message_validation.value:
                raise core.SOAPError(SOAP.Code.CLIENT, str(message_validation.errors[0]))
            soap_envelope = message_validation.validated_document
            soap_body_content = soap_envelope.Body.content()

            handler = self._find_handler_for_request(request, soap_body_content)

            # TODO return soap fault if header is required but missing in the input
            if soap_envelope.Header is not None:
                if handler.input_header:
                    request.soap_header = soap_envelope.Header.parse_as(handler.input_header)
                elif self.service.input_header:
                    request.soap_header = soap_envelope.Header.parse_as(self.service.input_header)

            request.method = handler

            input_validation = self._parse_input(handler, soap_body_content)
            if not input_validation.value:
                raise core.SOAPError(SOAP.Code.CLIENT, str(input_validation.errors[0]))
            validated_input = input_validation.validated_document

            request.soap_body = validated_input
        except core.SOAPError as ex:
            response = ex
        else:
            response = self.middleware()(request)

        if not isinstance(response, core.SoapboxResponse):
            response = core.SoapboxResponse(response)

        response.http_headers['content-type'] = SOAP.CONTENT_TYPE

        if isinstance(response.content, core.SOAPError):
            error = response.content
            response.http_content = SOAP.get_error_response(error.code, error.message, header=response.soap_header)
            response.http_status_code = 500
        else:
            tagname = uncapitalize(response.content.__class__.__name__)
            #self._validate_response(response.content, tagname)
            # TODO: handle validation results
            if isinstance(request.method.output, basestring):
                tagname = request.method.output
            else:
                tagname = uncapitalize(response.content.__class__.__name__)
            response.http_content = SOAP.Envelope.response(tagname, response.content, header=response.soap_header)
        return response


class WsgiSoapApplication(object):
    HTTP_500 = '500 Internal server error'
    HTTP_200 = '200 OK'
    HTTP_405 = '405 Method Not Allowed'

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def __call__(self, req_env, start_response, wsgi_url=None):
        content_length = int(req_env.get('CONTENT_LENGTH', 0))
        content = req_env['wsgi.input'].read(content_length)
        soap_request = core.SoapboxRequest(req_env, content)
        response = self.dispatcher.dispatch(soap_request)
        start_response(self._get_http_status(response.http_status_code), response.http_headers.items())
        return [response.http_content]

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
