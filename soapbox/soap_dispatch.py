# encoding: utf8

from __future__ import absolute_import

from lxml import etree

from .lib.attribute_dict import AttrDict
from .lib.result import ValidationResult
from .utils import uncapitalize
from soapbox.soap import SOAPError


__all__ = ['SOAPDispatcher', 'SoapboxRequest']

class DjangoCompatHeaders(object):
    def __init__(self, headers):
        self.headers = headers

    def get(self, key):
        assert key.startswith('HTTP_')
        header_key = key[5:]
        return self.headers.get(header_key)


class SoapboxRequest(object):
    def __init__(self, request, headers, method):
        self.request = request
        self.headers = headers
        self.method = method.upper()

    @property
    def META(self):
        return DjangoCompatHeaders(self.headers)


class SOAPDispatcher(object):
    def __init__(self, service):
        self.service = service

    def handle_request_for_wsdl(self, request):
        pass

    def _parse_soap_content(self, xml):
        SOAP = self.service.version
        # quick fix for "lxml does not support unicode strings with xml encoding declaration"
        if isinstance(xml, unicode):
            xml = xml.encode('utf-8')
        try:
            envelope = SOAP.Envelope.parsexml(xml)
        except etree.XMLSyntaxError as e:
            return ValidationResult(False, errors=(e,))
        return ValidationResult(True, validated_document=envelope)

    def _find_handler_for_request(self, request, message):
        SOAP = self.service.version
        soap_action = SOAP.determine_soap_action(request)
        root_tag = None
        if not soap_action:
            root_tag = self._find_root_tag(message)
        # TODO: handle invalid xml
        for method in self.service.methods:
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

    def _call_handler(self, soapbox_request, method, input_object):
        SOAP = self.service.version
        return_object = method.function(soapbox_request.request, input_object)
        if isinstance(return_object, SOAPError):
            error = return_object
            error_response = SOAP.get_error_response(error.faultcode, error.faultstring)
            return (error_response, True)

        tagname = uncapitalize(return_object.__class__.__name__)
        #self._validate_response(return_object, tagname)
        # TODO: handle validation results

        if isinstance(method.output, basestring):
            tagname = method.output
        return (SOAP.Envelope.response(tagname, return_object), False)

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
        error_text = unicode(first_error)
        fault_message = SOAP.get_error_response(SOAP.Code.CLIENT, error_text)
        return self.response(fault_message, is_error=True)

    def dispatch(self, soapbox_request, body_contents):
        if soapbox_request.method != 'POST':
            return AttrDict(
                status=400,
                content_type='text/plain',
                message='bad request',
            )
        SOAP = self.service.version
        message_validation = self._parse_soap_content(body_contents)
        if message_validation.value != True:
            return self.error_response(SOAP.Code.CLIENT, message_validation.errors)
        soap_envelope = message_validation.validated_document
        soap_request_message = soap_envelope.Body.content()

        handler = self._find_handler_for_request(soapbox_request, soap_request_message)
        # if not handler -> client error
        #  response = SOAP.get_error_response(SOAP.Code.CLIENT, str(e))

        input_validation = self._parse_input(handler, soap_request_message)
        if input_validation.value != True:
            return self.error_response(SOAP.Code.CLIENT, input_validation.errors)
        validated_input = input_validation.validated_document

        soap_response_message, is_error = self._call_handler(soapbox_request, handler, validated_input)
        # if not soap_response_message -> server error
        # SOAP.get_error_response(SOAP.Code.SERVER, str(e))
        return self.response(soap_response_message, is_error=is_error)
