# -*- coding: utf-8 -*-

from lxml import etree

from . import xsd
from . import namespaces as ns


ENVELOPE_NAMESPACE = ns.soap11_envelope
BINDING_NAMESPACE = ns.wsdl_soap
CONTENT_TYPE = 'text/xml'


# --- Functions ---------------------------------------------------------------
def determine_soap_action(request):
    if request.META.get('HTTP_SOAPACTION'):
        return request.META.get('HTTP_SOAPACTION').replace('"', '')
    elif request.META.get('HTTP_ACTION'):
        return request.META.get('HTTP_ACTION').replace('"', '')
    else:
        return None


def get_error_response(code, message, actor=None):
    fault = Fault(faultcode=code, faultstring=message, faultactor=actor)
    envelope = Envelope()
    envelope.Body = Body(Fault=fault)
    return envelope.xml('Envelope', namespace=ENVELOPE_NAMESPACE,
                        elementFormDefault=xsd.ElementFormDefault.QUALIFIED)


def parse_fault_message(fault):
    return fault.faultcode, fault.faultstring, fault.faultactor


def build_header(soapAction):
    return {'content-type': CONTENT_TYPE, 'SOAPAction': soapAction}


class Code:
    CLIENT = 'Client'
    SERVER = 'Server'


class Header(xsd.ComplexType):
    '''
    SOAP Envelope Header.
    '''
    pass


class Fault(xsd.ComplexType):
    '''
    SOAP Envelope Fault.
    '''
    faultcode = xsd.Element(xsd.String, namespace='')
    faultstring = xsd.Element(xsd.String, namespace='')
    faultactor = xsd.Element(xsd.String, namespace='', minOccurs=0)


class Body(xsd.ComplexType):
    '''
    SOAP Envelope Body.
    '''
    message = xsd.ClassNamedElement(xsd.NamedType, minOccurs=0)
    Fault = xsd.Element(Fault, minOccurs=0)

    def content(self):
        return etree.tostring(self._xmlelement[0], pretty_print=True)


class Envelope(xsd.ComplexType):
    '''
    SOAP Envelope.
    '''
    Header = xsd.Element(Header, nillable=True)
    Body = xsd.Element(Body)

    @classmethod
    def response(cls, tagname, return_object):
        envelope = Envelope()
        envelope.Body = Body()
        envelope.Body.message = xsd.NamedType(name=tagname, value=return_object)
        return envelope.xml('Envelope', namespace=ENVELOPE_NAMESPACE,
                elementFormDefault=xsd.ElementFormDefault.QUALIFIED)


SCHEMA = xsd.Schema(
    targetNamespace=ENVELOPE_NAMESPACE,
    elementFormDefault=xsd.ElementFormDefault.QUALIFIED,
    complexTypes=[Header, Body, Envelope, Fault],
)
