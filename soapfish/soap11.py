import enum

from . import namespaces as ns, xsd

ENVELOPE_NAMESPACE = ns.soap11_envelope
BINDING_NAMESPACE = ns.wsdl_soap
CONTENT_TYPE = 'text/xml'
NAME = 'soap11'


# --- Functions ---------------------------------------------------------------
def determine_soap_action(request):
    if request.environ.get('SOAPACTION'):
        return request.environ.get('SOAPACTION').replace('"', '')
    elif request.environ.get('ACTION'):
        return request.environ.get('ACTION').replace('"', '')
    else:
        return None


def build_http_request_headers(soapAction):
    return {'Content-Type': CONTENT_TYPE, 'SOAPAction': soapAction}


def get_error_response(code, message, actor=None, header=None):
    return Envelope.error_response(code, message, actor=actor, header=header)


def parse_fault_message(fault):
    return fault.faultcode, fault.faultstring, fault.faultactor


class Code(str, enum.Enum):
    CLIENT = 'Client'
    SERVER = 'Server'


class Header(xsd.ComplexType):
    def accept(self, value):
        return value

    def parse_as(self, ContentType):
        return ContentType.parse_xmlelement(self._xmlelement)

    def render(self, parent, instance, namespace=None, elementFormDefault=None):
        return super().render(parent, instance, instance.SCHEMA.targetNamespace, elementFormDefault)


class Fault(xsd.ComplexType):
    faultcode = xsd.Element(xsd.String, namespace='')
    faultstring = xsd.Element(xsd.String, namespace='')
    faultactor = xsd.Element(xsd.String, namespace='', minOccurs=0)


class Body(xsd.ComplexType):
    message = xsd.ClassNamedElement(xsd.NamedType, minOccurs=0)
    Fault = xsd.Element(Fault, minOccurs=0)

    def parse_as(self, ContentType):
        return ContentType.parse_xmlelement(self._xmlelement[0])

    def content(self):
        return self._xmlelement[0]


class Envelope(xsd.ComplexType):
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
                            elementFormDefault=xsd.ElementFormDefault.QUALIFIED, pretty_print=False)

    @classmethod
    def error_response(cls, code, message, header=None, actor=None):
        envelope = cls()
        if header is not None:
            envelope.Header = header
        envelope.Body = Body()
        envelope.Body.Fault = Fault(faultcode=code, faultstring=message, faultactor=actor)
        return envelope.xml('Envelope', namespace=ENVELOPE_NAMESPACE,
                            elementFormDefault=xsd.ElementFormDefault.QUALIFIED, pretty_print=False)


SCHEMA = xsd.Schema(
    targetNamespace=ENVELOPE_NAMESPACE,
    elementFormDefault=xsd.ElementFormDefault.QUALIFIED,
    complexTypes=[Header, Body, Envelope, Fault],
)
