import xsd
import xsdspec

class SOAP_Binding(xsd.ComplexType):
    NAMESPACE = "http://schemas.xmlsoap.org/wsdl/soap/"
    ELEMENT_FORM_DEFAULT = xsd.ElementFormDefault.QUALIFIED
    style = xsd.Attribute(xsd.String)
    transport = xsd.Attribute(xsd.String)
    
class SOAP_Operation(xsd.ComplexType):
    NAMESPACE = "http://schemas.xmlsoap.org/wsdl/soap/"
    ELEMENT_FORM_DEFAULT = xsd.ElementFormDefault.QUALIFIED
    soapAction = xsd.Attribute(xsd.String)
    
class SOAP_Body(xsd.ComplexType):
    NAMESPACE = "http://schemas.xmlsoap.org/wsdl/soap/"
    ELEMENT_FORM_DEFAULT = xsd.ElementFormDefault.QUALIFIED
    use = xsd.Attribute(xsd.String)
    
class SOAP_Address(xsd.ComplexType):
    NAMESPACE = "http://schemas.xmlsoap.org/wsdl/soap/"
    ELEMENT_FORM_DEFAULT = xsd.ElementFormDefault.QUALIFIED
    location = xsd.Attribute(xsd.String)
    
class Types(xsd.ComplexType):
    schema = xsd.Element(xsdspec.Schema)
    
class Part(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    element = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    type = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    
class Message(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    part = xsd.Element(Part)

class Input(xsd.ComplexType):
    message = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    body = xsd.Element(SOAP_Body, minOccurs=0)
    
class Operation(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    input = xsd.Element(Input)
    output = xsd.Element(Input)
    body = xsd.Element(SOAP_Body)
    operation = xsd.Element(SOAP_Operation)
    
class PortType(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    operation = xsd.Element(Operation)
    
class Binding(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    type = xsd.Attribute(xsd.String)
    binding = xsd.Element(SOAP_Binding)
    operation = xsd.Element(Operation)
    
class Port(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    binding = xsd.Attribute(xsd.String)
    address = xsd.Element(SOAP_Address)
      
class Service(xsd.ComplexType):
    documentation = xsd.Element(xsd.String)
    port = xsd.Element(Port)
    
class Definitions(xsd.ComplexType):
    targetNamespace = xsd.Attribute(xsd.String)
    types = xsd.Element(Types)
    messages = xsd.ListElement(Message,"message")
    portTypes = xsd.ListElement(PortType, "portType")
    bindings = xsd.ListElement(Binding, "binding")
    services = xsd.ListElement(Service,"service")
    
    @classmethod
    def get_by_name(cls, _list, fullname):
        name = fullname.split(":")[-1]
        for item in _list:
            if item.name == name:
                return item
        raise ValueError("Item '%s' not found in list:%s" % (name, _list))
    
    
SCHEMA = xsd.Schema(
    targetNamespace = "http://schemas.xmlsoap.org/wsdl/",
    elementFormDefault = xsd.ElementFormDefault.QUALIFIED,
    simpleTypes = [],
    attributeGroups = [],
    groups = [],
    complexTypes = [Types, Part, Message, Input, Operation, PortType, Binding,
                    Port, Service, Definitions],
    elements = {})
    
    
    
    
        
            
    
    
