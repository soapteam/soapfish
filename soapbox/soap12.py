# -*- coding: utf-8 -*-

from lxml import etree

from . import namespaces as ns
from . import soap11
from . import xsd


ENVELOPE_NAMESPACE = ns.soap12_envelope
BINDING_NAMESPACE = ns.wsdl_soap12
CONTENT_TYPE = 'application/soap+xml'
NAME = 'soap12'


# --- Functions ---------------------------------------------------------------
def determine_soap_action(request):
    content_types = request.environ.get('CONTENT_TYPE','').split(';')
    for content_type in content_types:
        if content_type.strip(' ').startswith('action='):
            action = content_type.split('=')[1]
            return action.replace('"', '')
    return None


def build_http_request_headers(soapAction):
    return {'content-type': CONTENT_TYPE + ';action="%s"' % soapAction}


def get_error_response(code, message, actor=None, header=None):
    return Envelope.error_response(code, message, actor=actor, header=header)


def parse_fault_message(fault):
    return fault.Code.Value, fault.Reason.Text, fault.Role


class Header(soap11.Header):
    pass


class Code(xsd.ComplexType):
    CLIENT = 'ns0:Sender'
    SERVER = 'ns0:Receiver'
    Value = xsd.Element(xsd.String)


class LanguageString(xsd.String):

    def render(self, parent, value, namespace, elementFormDefault):
        parent.text = self.xmlvalue(value)
        parent.set('{%s}lang' % ns.xml, 'en')


class Reason(xsd.ComplexType):
    Text = xsd.Element(LanguageString)


class Fault(xsd.ComplexType):
    '''
    SOAP Envelope Fault.
    '''
    Code = xsd.Element(Code)
    Reason = xsd.Element(Reason)
    Role = xsd.Element(xsd.String, minOccurs=0)


class Body(soap11.Body):
    '''
    SOAP Envelope Body.
    '''
    message = xsd.ClassNamedElement(xsd.NamedType, minOccurs=0)
    Fault = xsd.Element(Fault, minOccurs=0)


class Envelope(xsd.ComplexType):
    '''
    SOAP Envelope.
    '''
    Header = xsd.Element(Header, nillable=True)
    Body = xsd.Element(Body)

    @classmethod
    def response(cls, tagname, return_object, header=None):
        envelope = cls()
        if header is not None:
            envelope.Header = header
        envelope.Body = Body()
        envelope.Body.message = xsd.NamedType(name=tagname, value=return_object)
        return envelope.xml('Envelope', namespace=ENVELOPE_NAMESPACE,
            elementFormDefault=xsd.ElementFormDefault.QUALIFIED)

    @classmethod
    def error_response(cls, code, message, header=None, actor=None):
        envelope = cls()
        if header is not None:
            envelope.Header = header
        envelope.Body = Body()
        code = Code(Value=code)
        reason = Reason(Text=message)
        envelope.Body.Fault = Fault(Code=code, Reason=reason, Role=actor)
        return envelope.xml('Envelope', namespace=ENVELOPE_NAMESPACE,
            elementFormDefault=xsd.ElementFormDefault.QUALIFIED)


SCHEMA = xsd.Schema(
    targetNamespace=ENVELOPE_NAMESPACE,
    elementFormDefault=xsd.ElementFormDefault.QUALIFIED,
    complexTypes=[Header, Body, Envelope, Code, Reason, Fault],
)
