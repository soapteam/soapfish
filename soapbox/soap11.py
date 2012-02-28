from lxml import etree
import xsd

ENVELOPE_NAMESPACE = "http://schemas.xmlsoap.org/soap/envelope/"
BINDING_NAMESPACE = "http://schemas.xmlsoap.org/wsdl/soap/"
CONTENT_TYPE = "text/xml"
class Code:
    CLIENT = "Client"
    SERVER = "Server"


def determin_soap_action(request):
    if request.META.get("HTTP_SOAPACTION"):
        return request.META.get("HTTP_SOAPACTION").replace('"','')
    elif request.META.get("HTTP_ACTION"):
        return request.META.get("HTTP_ACTION").replace('"','')
    else:
        return None

def get_error_response(code,message):
    fault = Fault(faultcode="Client", faultstring=message)
    envelope = Envelope()
    envelope.Body = Body(Fault=fault)
    return envelope.xml("Envelope",namespace=ENVELOPE_NAMESPACE,
                        elementFormDefault=xsd.ElementFormDefault.QUALIFIED)

def parse_fault_message(fault):
    return fault.faultcode,fault.faultstring

def build_header(soapAction):
    return {"content-type" : CONTENT_TYPE,
            "SOAPAction"   : soapAction}

class Header(xsd.ComplexType):
    """SOAP Envelope Header."""
    pass

class Fault(xsd.ComplexType):
    """SOAP Envelope Fault."""
    faultcode = xsd.Element(xsd.String,namespace="")
    faultstring = xsd.Element(xsd.String,namespace="")

class Body(xsd.ComplexType):
    """SOAP Envelope Body."""
    message = xsd.ClassNamedElement(xsd.NamedType, minOccurs=0)
    Fault = xsd.Element(Fault, minOccurs=0)
    def content(self):
        return etree.tostring(self._xmlelement[0], pretty_print=True)



class Envelope(xsd.ComplexType):
    """SOAP Envelope."""
    Header = xsd.Element(Header, nillable=True)
    Body = xsd.Element(Body)

    @classmethod
    def reponse(cls, tagname,return_object):
        envelope = Envelope()
        envelope.Body = Body()
        envelope.Body.message = xsd.NamedType(name=tagname,value=return_object)
        return envelope.xml("Envelope",namespace=ENVELOPE_NAMESPACE,
                elementFormDefault=xsd.ElementFormDefault.QUALIFIED)

SCHEMA = xsd.Schema(
    targetNamespace = ENVELOPE_NAMESPACE,
    elementFormDefault = xsd.ElementFormDefault.QUALIFIED,
    complexTypes = [Header, Body, Envelope, Fault])
