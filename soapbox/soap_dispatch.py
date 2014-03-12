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
from .py2xsd import generate_xsd
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
        schema = generate_xsd(self.service.schema)
        self.xmlschema = etree.XMLSchema(schema)

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
            # note : no validation is performed
            envelope = SOAP.Envelope.parsexml(xml)
        except etree.XMLSyntaxError as e:
            raise core.SOAPError(SOAP.Code.CLIENT, repr(e))
        # Actually this is more a stopgap measure than a real fix. The real
        # fix is to change SOAP.Envelope/ComplexType so it raise some kind of
        # validation error. A missing SOAP body is not allowed by the SOAP
        # specs (according to my interpretation):
        # SOAP 1.1: http://schemas.xmlsoap.org/soap/envelope/
        # SOAP 1.2: http://www.w3.org/2003/05/soap-envelope/
        if envelope.Body is None:
            raise core.SOAPError(SOAP.Code.CLIENT, "Missing SOAP body")
        return envelope

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

    def _parse_header(self, handler, soap_header):
        # TODO return soap fault if header is required but missing in the input
        if soap_header is not None:
            if handler.input_header:
                return soap_header.parse_as(handler.input_header)
            elif self.service.input_header:
                return soap_header.parse_as(self.service.input_header)

    def _parse_input(self, method, message):
        input_parser = method.input
        if isinstance(method.input, basestring):
            element = self.service.schema.elements[method.input]
            input_parser = element._type
        return input_parser.parse_xmlelement(message)

    def _validate_response(self, return_object, tagname):
        return_object.xml(tagname, namespace=self.service.schema.targetNamespace,
                          elementFormDefault=self.service.schema.elementFormDefault,
                          schema=self.service.schema)  # Validation.

    def _validate_header(self, soap_header):
        SOAP = self.service.version
        if soap_header is not None:
            for children in soap_header._xmlelement.getchildren():
                self.xmlschema.assertValid(children)

    def _validate_body(self, soap_body):
        SOAP = self.service.version
        self.xmlschema.assertValid(soap_body.content())

    def _validate_input(self, envelope):
        self._validate_header(envelope.Header)
        self._validate_body(envelope.Body)

    def dispatch(self, request):
        if request.environ['REQUEST_METHOD'] != 'POST':
            return core.SoapboxResponse('bad request', http_status_code=400,
                http_content='bad_request', http_headers={'CONTENT_TYPE': 'text/plain'})

        request.dispatcher = self
        SOAP = self.service.version

        try:
            soap_envelope = self._parse_soap_content(request.content)
            soap_body_content = soap_envelope.Body.content()
            soap_header = soap_envelope.Header

            try:
                self._validate_input(soap_envelope)
            except (etree.XMLSyntaxError, etree.DocumentInvalid) as e:
                raise core.SOAPError(SOAP.Code.CLIENT, repr(e))

            request.method = self._find_handler_for_request(request, soap_body_content)
            request.soap_header = self._parse_header(request.method, soap_header)
            request.soap_body = self._parse_input(request.method, soap_body_content)
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
