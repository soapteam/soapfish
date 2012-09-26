# -*- coding: utf-8 -*-
################################################################################

'''
SOAP protocol implementation, dispatchers and client stub.
'''

################################################################################
# Imports


import httplib2
import logging
import os

from urlparse import urlparse

from lxml import etree

from . import settings, soap11, soap12, xsd
from .utils import CustomFaultValueError, uncapitalize


################################################################################
# Constants


SOAP_HTTP_Transport = 'http://schemas.xmlsoap.org/soap/http'


################################################################################
# Globals


logger = logging.getLogger('soapbox')
logger.addHandler(logging.NullHandler())


################################################################################
# Classes


class SOAPVersion:
    '''
    '''
    SOAP12 = soap12
    SOAP11 = soap11

    @classmethod
    def get_version(cls, namespace):
        '''
        '''
        if namespace == cls.SOAP11.ENVELOPE or namespace == cls.SOAP11.BINDING:
            return cls.SOAP11
        elif  namespace == cls.SOAP12.ENVELOPE or namespace == cls.SOAP12.BINDING:
            return cls.SOAP11
        else:
            raise ValueError("SOAP version with namespace '%s' is not supported." % namespace)

    @classmethod
    def get_version_name(cls, namespace):
        '''
        '''
        version = cls.get_version(namespace)
        return version.__name__


class SOAPError(Exception):
    '''
    '''
    pass


class Service(object):
    '''
    Describes service aggregating informations required for dispatching and
    WSDL generation.
    '''

    def __init__(self, targetNamespace, location, schema, methods,
                 version=SOAPVersion.SOAP11, name='Service', input_message_appendix='Input', output_message_appendix='Output'):
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

        self.input_message_appendix = input_message_appendix
        self.output_message_appendix = output_message_appendix

    def get_method(self, operationName):
        '''
        '''
        return filter(lambda m: m.operationName == operationName, self.methods)[0]


class Stub(object):
    '''
    Client stub. Handles only document style calls.
    '''
    SERVICE = None
    SCHEME = 'http'
    HOST = 'www.example.net'

    def __init__(self, username=None, password=None, service=None, location=None, base_url=None):
        '''
        '''
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

    def _handle_response(self, method, response, content):
        '''
        '''
        SOAP = self.SERVICE.version
        envelope = SOAP.Envelope.parsexml(content)

        if envelope.Body.Fault:
            code, message = SOAP.parse_fault_message(envelope.Body.Fault)
            error = 'Fault Code: %s, Fault Message: %s' % (code, message)
            logger.error(error)
            raise SOAPError(error)

        message = envelope.Body.content()

        if isinstance(method.output, basestring):
            element = self.SERVICE.schema.get_element_by_name(method.output)
            _type = element._type
        else:
            _type = method.output

        if self.SERVICE.schema:
            return _type.parsexml(message, self.SERVICE.schema)
        else:
            return _type.parsexml(message)

    def call(self, operationName, parameter):
        '''
        :raises: lxml.etree.XMLSyntaxError -- validation problems.
        '''
        SOAP = self.SERVICE.version
        method = self.SERVICE.get_method(operationName)
        if isinstance(method.input, basestring):
            tagname = method.input
        else:
            tagname = uncapitalize(parameter.__class__.__name__)
        parameter.xml(tagname,
                      schema=self.SERVICE.schema,
                      namespace=parameter.SCHEMA.targetNamespace,
                      elementFormDefault=parameter.SCHEMA.elementFormDefault)

        disable_validation = not os.path.exists(settings.CA_CERTIFICATE_FILE)
        http = httplib2.Http(
            ca_certs=settings.CA_CERTIFICATE_FILE,
            disable_ssl_certificate_validation=disable_validation,
            timeout=settings.REQUEST_TIMEOUT,
        )
        if self.username:
            http.add_credentials(self.username, self.password)

        method = self.SERVICE.get_method(operationName)
        headers = SOAP.build_header(method.soapAction)
        envelope = SOAP.Envelope.response(tagname, parameter)

        logger.info('Request \'%s\'...' % self.location)
        logger.debug('Request Headers:\n\n%s\n' % headers)
        logger.debug('Request Envelope:\n\n%s\n' % envelope)
        response, content = http.request(self.location, 'POST',
             body=envelope, headers=headers)
        logger.debug('Response Headers:\n\n%s\n' % response)
        logger.debug('Response Envelope:\n\n%s\n' % content)

        return self._handle_response(method, response, content)


################################################################################
# Dispatcher


def get_django_dispatch(service):
    '''
    '''

    def call_the_method(request, message, soap_action):
        '''
        '''
        for method in service.methods:
            if soap_action != method.soapAction:
                continue

            if isinstance(method.input, basestring):
                element = service.schema.elements[method.input]
                input_object = element._type.parsexml(message, service.schema)
            else:
                input_object = method.input.parsexml(message, service.schema)

            return_object = method.function(request, input_object)
            try:
                tagname = uncapitalize(return_object.__class__.__name__)
                return_object.xml(tagname, namespace=service.schema.targetNamespace,
                                  elementFormDefault=service.schema.elementFormDefault,
                                  schema=service.schema)  # Validation.
            except Exception, e:
                raise ValueError(e)

            if isinstance(method.output, basestring):
                tagname = method.output
            else:
                tagname = uncapitalize(return_object.__class__.__name__)
            return tagname, return_object
        raise ValueError('Method not found!')

    def django_dispatch(request):
        '''
        '''
        from django.http import HttpResponse
        from . import py2wsdl

        SOAP = service.version

        if request.method == 'GET' and 'wsdl' in request.GET:
            wsdl = py2wsdl.generate_wsdl(service)
            return HttpResponse(wsdl, mimetype='text/xml')

        try:
            try:
                xml = request.raw_post_data
                envelope = SOAP.Envelope.parsexml(xml)
                message = envelope.Body.content()
                soap_action = SOAP.determin_soap_action(request)
                tagname, return_object = call_the_method(request, message, soap_action)
                soap_message = SOAP.Envelope.response(tagname, return_object)
                return HttpResponse(soap_message, content_type=SOAP.CONTENT_TYPE)
            except CustomFaultValueError as e:
                # okay here it gets hacky
                # first create an empty response to check at the end, if we found a custom error to return
                response = None
                # then check all defined methods
                for method in service.methods:
                    # soap_action done is not the current method? One more round!
                    if soap_action != method.soapAction:
                        continue
                    # check if defined faults of method are in a list (we can have more than one fault per method)
                    if isinstance(method.faults, list):
                        # now check against the defined faults
                        for fault in method.faults:
                            # if fault is defined in elements of schema and the defined response fault type is the one raised in the exception, we got it
                            if fault in service.schema.elements and service.schema.elements[fault]._type.__class__ == e.complex_type_instance.__class__:
                                # here is the really hacky part
                                # because xsd.ComplexType has dynamic Fields, a little messing around with its meta class is needed.
                                # Here a custom ComplexType sub class is generated with a field named as the found fault and type Element(raised complex type)
                                class MetaClass(xsd.Complex_PythonType):
                                    def __new__(cls, name, bases, attrs):
                                        attrs[fault] = xsd.Element(
                                            service.schema.elements[fault]._type.__class__,
                                            namespace=service.schema.elements[fault]._type.__class__.SCHEMA.targetNamespace
                                        )
                                        return super(MetaClass, cls).__new__(cls, name, bases, attrs)

                                # This class does not very much, it just gets the meta class
                                class FaultDetail(xsd.ComplexType):
                                    __metaclass__ = MetaClass

                                # and here the response is generated. It looks like:
                                #
                                # <ns0:Envelope xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/">
                                #    <ns0:Body>
                                #       <ns0:Fault>
                                #          <faultcode>Client</faultcode>
                                #          <faultstring>{{ exception message (as with ValueError) }}</faultstring>
                                #          <detail>
                                #             <ns0:{{ fault element name }} xmlns:ns0="{{ fault element namespace }}">
                                #                {{ rendered complex type }}
                                #             </ns0:{{ fault element name }}>
                                #          </detail>
                                #       </ns0:Fault>
                                #    </ns0:Body>
                                # </ns0:Envelope>
                                response = SOAP.get_error_response(SOAP.Code.CLIENT, str(e), detail=FaultDetail(**{fault: e.complex_type_instance}))
                                break
                    if response is not None:
                        break
                if response is None:
                    raise ValueError(str(e))
        except (ValueError, etree.XMLSyntaxError) as e:
            response = SOAP.get_error_response(SOAP.Code.CLIENT, str(e))
        except Exception, e:
            response = SOAP.get_error_response(SOAP.Code.SERVER, str(e))
        return HttpResponse(response, content_type=SOAP.CONTENT_TYPE)

    return django_dispatch


################################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
