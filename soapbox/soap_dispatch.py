# encoding: utf8

from __future__ import absolute_import

import logging
from lxml import etree
import six

from . import soap
from .lib.attribute_dict import AttrDict
from .lib.result import ValidationResult
from .utils import uncapitalize
from .soap import SOAPError

basestring = six.string_types

__all__ = ['SOAPDispatcher', 'SoapboxRequest']

logger = logging.getLogger(__name__)


class SoapboxResponse(object):
    def __init__(self, content, soap_header=None):
        self.content = content
        self.soap_header = soap_header


class SoapboxRequest(object):
    def __init__(self, environ, content):
        self.environ = environ
        self.content = content
        self.soap_header = None
        self.response = SoapboxResponse(self)


class SOAPDispatcher(object):
    def __init__(self, service):
        self.service = service

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

    def call_wrapper(self, method, soapbox_request, input_object):
        return method.function(soapbox_request, input_object)

    def _call_handler(self, soapbox_request, method, input_object):
        SOAP = self.service.version
        response = self.call_wrapper(method, soapbox_request, input_object)
        if not isinstance(response, SoapboxResponse):
            response = SoapboxResponse(response)
        if isinstance(response.content, SOAPError):
            error = response.content
            error_response = SOAP.get_error_response(error.faultcode, error.faultstring, header=response.soap_header)
            return (error_response, True)

        tagname = uncapitalize(response.content.__class__.__name__)
        #self._validate_response(response.content, tagname)
        # TODO: handle validation results

        if isinstance(method.output, basestring):
            tagname = method.output
        return (SOAP.Envelope.response(tagname, response.content, header=response.soap_header), False)

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

    def dispatch(self, soapbox_request):
        if soapbox_request.environ['REQUEST_METHOD'] != 'POST':
            return AttrDict(
                status=400,
                content_type='text/plain',
                message='bad request',
            )
        SOAP = self.service.version
        message_validation = self._parse_soap_content(soapbox_request.content)
        if not message_validation.value:
            return self.error_response(SOAP.Code.CLIENT, message_validation.errors)
        soap_envelope = message_validation.validated_document
        soap_request_message = soap_envelope.Body.content()

        handler = self._find_handler_for_request(soapbox_request, soap_request_message)
        # if not handler -> client error
        #  response = SOAP.get_error_response(SOAP.Code.CLIENT, str(e))

        # TODO return soap fault if header is required but missing in the input
        if soap_envelope.Header is not None:
            if handler.input_header:
                soapbox_request.soap_header = soap_envelope.Header.parse_as(handler.input_header)
            elif self.service.input_header:
                soapbox_request.soap_header = soap_envelope.Header.parse_as(self.service.input_header)

        input_validation = self._parse_input(handler, soap_request_message)
        if not input_validation.value:
            return self.error_response(SOAP.Code.CLIENT, input_validation.errors)
        validated_input = input_validation.validated_document

        # LATER: the dispatcher should be able to also catch arbitrary
        # exceptions from the handler. At the same time the caller should be
        # able to install custom hooks for these exceptions (e.g. custom
        # traceback logging) and we should support popular debugging middlewares
        # somehow.
        soap_response_message, is_error = self._call_handler(soapbox_request, handler, validated_input)

        return self.response(soap_response_message, is_error=is_error)


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
        soap_request = SoapboxRequest(req_env, content)
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
