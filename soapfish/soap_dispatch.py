import functools
import logging
import re
import string
from urllib.parse import parse_qs

from lxml import etree

from . import py2wsdl, py2xsd, wsa
from .core import SOAPError, SOAPRequest, SOAPResponse
from .utils import uncapitalize, walk_schema_tree

__all__ = ['SOAPDispatcher']

logger = logging.getLogger(__name__)


def call_method(request):
    request.dispatcher._prepare_request(request)
    response = request.method.function(request, request.soap_body)
    return response if isinstance(response, SOAPResponse) else SOAPResponse(response)


class SOAPDispatcher:
    def __init__(self, service, middlewares=None, hooks=None, wsdl=None, xsds=None, strict_soap_header=True):
        # If set, strict_soap_header causes an exception to be raised if a header part is not in the schema.
        self.service = service
        self.middlewares = middlewares if middlewares is not None else []
        self.schema_validator = py2xsd.schema_validator(self.service.schemas)

        if hooks is None:
            hooks = {}
        else:
            for hook in hooks:
                if not re.match(r'(soap|wsdl|xsd)-(request|response)', hook):
                    raise KeyError(f'Invalid dispatcher hook name: {hook}')
        self.hooks = hooks

        if wsdl is None:
            wsdlelement = py2wsdl.generate_wsdl(self.service)
            self._rewrite_locations(wsdlelement)
            wsdl = etree.tostring(wsdlelement, pretty_print=True)
        self.wsdl = wsdl

        if xsds is None:
            def callback(item):
                xsdelement = py2xsd.generate_xsd(item)
                self._rewrite_locations(xsdelement)
                return etree.tostring(xsdelement, pretty_print=True)
            xsds = walk_schema_tree(self.service.schemas, callback)
        self.xsds = xsds

        self.strict_soap_header = strict_soap_header

    def middleware(self, i=0):
        if i == len(self.middlewares):
            # at the end call the method
            return call_method
        return functools.partial(self.middlewares[i], next_call=self.middleware(i + 1))

    def _parse_soap_content(self, xml):
        SOAP = self.service.version
        try:
            # note : no validation is performed
            envelope = SOAP.Envelope.parsexml(xml)
        except etree.XMLSyntaxError as e:
            raise SOAPError(SOAP.Code.CLIENT, f'{e.__class__.__name__}: {e}') from e
        # Actually this is more a stopgap measure than a real fix. The real
        # fix is to change SOAP.Envelope/ComplexType so it raises some kind of
        # validation error. A missing SOAP body is not allowed by the SOAP
        # specs (according to my interpretation):
        # SOAP 1.1: http://schemas.xmlsoap.org/soap/envelope/
        # SOAP 1.2: http://www.w3.org/2003/05/soap-envelope/
        if envelope.Body is None:
            raise SOAPError(SOAP.Code.CLIENT, 'Missing SOAP body')
        return envelope

    def _find_handler_for_request(self, request, body):
        # TODO: Properly handle invalid XML.
        SOAP = self.service.version

        action = SOAP.determine_soap_action(request)
        root_tag = etree.QName(body.tag).localname

        if action:
            logger.debug('Finding handler using SOAP action found in HTTP headers: %s', action)
            try:
                return next(m for m in self.service.methods if m.soapAction == action)
            except StopIteration as e:
                raise SOAPError(SOAP.Code.CLIENT, f'Invalid SOAP action: {action}') from e

        else:
            logger.debug('Finding handler using root tag of the SOAP body: %s', root_tag)
            try:
                return next(m for m in self.service.methods if m.input == root_tag)
            except StopIteration:
                pass  # fall through and check for substitution group element
            try:
                # FIXME: Improve handling of namespaces to be less hacky...
                e = next(e for s in self.service.schemas for n, e in s.elements.items() if n == root_tag)
                return next(m for m in self.service.methods if m.input == e.substitutionGroup.split(':')[-1])
            except StopIteration as e:
                raise SOAPError(SOAP.Code.CLIENT, f'Missing SOAP action and invalid root tag: {root_tag}') from e

    def _parse_header(self, handler, soap_header):
        # TODO return soap fault if header is required but missing in the input
        if soap_header is None:
            return None
        if handler.input_header:
            return soap_header.parse_as(handler.input_header)
        elif self.service.input_header:
            return soap_header.parse_as(self.service.input_header)

    def _parse_input(self, method, message):
        input_parser = method.input
        if isinstance(method.input, str):
            element = self.service.find_element_by_name(method.input)
            input_parser = element._type
        return input_parser.parse_xmlelement(message)

    def _validate_response(self, return_object, tagname):
        # XXX: Lookup of schema is untested as method not currently in use.
        schema = return_object.SCHEMA
        assert schema in self.service.schemas
        return_object.xml(tagname, schema=schema,
                          namespace=schema.targetNamespace,
                          elementFormDefault=schema.elementFormDefault)

    def _validate_header(self, soap_header):
        if soap_header is None:
            return
        for children in soap_header._xmlelement.getchildren():
            namespace = children.nsmap.get(children.prefix)
            if namespace == wsa.NAMESPACE:
                wsa.XML_SCHEMA.assertValid(children)
            else:
                try:
                    self.schema_validator(children)
                except (etree.DocumentInvalid, etree.XMLSyntaxError):
                    if self.strict_soap_header:
                        raise

    def _validate_body(self, soap_body):
        self.schema_validator(soap_body.content())

    def _validate_input(self, envelope):
        self._validate_header(envelope.Header)
        self._validate_body(envelope.Body)

    def _prepare_request(self, request):
        SOAP = self.service.version

        soap_envelope = self._parse_soap_content(request.http_content)
        soap_header = soap_envelope.Header
        soap_body = soap_envelope.Body.content()

        try:
            self._validate_input(soap_envelope)
        except (etree.DocumentInvalid, etree.XMLSyntaxError) as e:
            raise SOAPError(SOAP.Code.CLIENT, f'{e.__class__.__name__}: {e}') from e

        request.method = self._find_handler_for_request(request, soap_body)
        request.soap_header = self._parse_header(request.method, soap_header)
        request.soap_body = self._parse_input(request.method, soap_body)

    def dispatch(self, request):
        request_method = request.environ.get('REQUEST_METHOD', '')
        qs = request.environ.get('QUERY_STRING', '')
        qs = parse_qs(qs, keep_blank_values=True)
        if request_method == 'GET' and qs.keys() & {'wsdl', 'singleWsdl'}:
            return self.handle_wsdl_request(request)
        elif request_method == 'GET' and 'xsd' in qs:
            return self.handle_xsd_request(request)
        elif request_method == 'POST':
            return self.handle_soap_request(request)
        else:
            return SOAPResponse('bad request', http_status_code=400, http_content='bad_request',
                                http_headers={'Content-Type': 'text/plain'})

    def handle_soap_request(self, request):
        request = self._call_hook('soap-request', dispatcher=self, request=request)
        request.dispatcher = self
        SOAP = self.service.version

        try:
            response = self.middleware()(request)
        except SOAPError as e:
            response = e

        if not isinstance(response, SOAPResponse):
            response = SOAPResponse(response)

        response.http_headers['Content-Type'] = SOAP.CONTENT_TYPE

        if isinstance(response.soap_body, SOAPError):
            error = response.soap_body
            response.http_content = SOAP.get_error_response(error.code, error.message, header=response.soap_header)
            response.http_status_code = 500
        else:
            # tagname = uncapitalize(response.soap_body.__class__.__name__)
            # self._validate_response(response.soap_body, tagname)
            # TODO: handle validation results
            if isinstance(request.method.output, str):
                tagname = request.method.output
            else:
                tagname = uncapitalize(response.content.__class__.__name__)
            response.http_content = SOAP.Envelope.response(tagname, response.soap_body, header=response.soap_header)

        return self._call_hook('soap-response', dispatcher=self, request=request, response=response)

    def handle_wsdl_request(self, request):
        request = self._call_hook('wsdl-request', dispatcher=self, request=request)
        scheme = request.environ.get('X_FORWARDED_PROTO', request.environ.get('wsgi.url_scheme', 'http'))
        host = request.environ.get('HTTP_HOST')
        wsdl = self.wsdl
        if scheme and host:
            wsdl = string.Template(wsdl.decode()).safe_substitute(scheme=scheme, host=host).encode()
        response = SOAPResponse('wsdl', http_content=wsdl, http_headers={'Content-Type': 'text/xml'})
        return self._call_hook('wsdl-response', dispatcher=self, request=request, response=response)

    def handle_xsd_request(self, request):
        request = self._call_hook('xsd-request', dispatcher=self, request=request)
        qs = request.environ.get('QUERY_STRING')
        qs = parse_qs(qs, keep_blank_values=True)
        try:
            xsd = self.xsds[qs['xsd'][0] or 'xsd']
        except KeyError:
            response = SOAPResponse('not found', http_status_code=404, http_content='not_found',
                                    http_headers={'Content-Type': 'text/plain'})
        else:
            response = SOAPResponse('xsd', http_content=xsd, http_headers={'Content-Type': 'text/xml'})

        return self._call_hook('wsdl-response', dispatcher=self, request=request, response=response)

    def _rewrite_locations(self, element):
        for e in element.xpath('//xsd:import|//xsd:include', namespaces=element.nsmap):
            e.attrib['schemaLocation'] = '?xsd=%s' % e.attrib['schemaLocation']

    def _call_hook(self, name, **kw):
        hook = self.hooks.get(name)
        obj = hook(**kw) if hook is not None else kw[name.split('-').pop()]
        if name.endswith('-request') and not isinstance(obj, SOAPRequest):
            raise TypeError('Request hooks must return a SOAPRequest.')
        if name.endswith('-response') and not isinstance(obj, SOAPResponse):
            raise TypeError('Response hooks must return a SOAPResponse.')
        return obj


class WsgiSoapApplication:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def __call__(self, req_env, start_response, wsgi_url=None):
        content_length = int(req_env.get('CONTENT_LENGTH', '') or 0)
        content = req_env['wsgi.input'].read(content_length)
        soap_request = SOAPRequest(req_env, content)
        response = self.dispatcher.dispatch(soap_request)
        start_response(response.http_status_text, list(response.http_headers.items()))
        return [response.http_content]
