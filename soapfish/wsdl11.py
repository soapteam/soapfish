from . import namespaces as ns, xsd, xsdspec

# FIXME: With the current implementation of schema we cannot share classes
#        between different schema so we duplicate classes to soapfish.wsdl12

# Notes:
# ------
#
# 1. Only optional for <wsdl:operation> under <wsdl:portType>
# 2. Only required for <wsdl:operation> under <wsdl:portType>


class SOAP_Binding(xsd.ComplexType):
    ELEMENT_FORM_DEFAULT = xsd.ElementFormDefault.QUALIFIED
    style = xsd.Attribute(xsd.String(enumeration=['document', 'rpc']), default='document', use=xsd.Use.OPTIONAL)
    transport = xsd.Attribute(xsd.AnyURI)


class SOAP_Operation(xsd.ComplexType):
    ELEMENT_FORM_DEFAULT = xsd.ElementFormDefault.QUALIFIED
    soapAction = xsd.Attribute(xsd.AnyURI, use=xsd.Use.OPTIONAL)
    style = xsd.Attribute(xsd.String(enumeration=['document', 'rpc']), use=xsd.Use.OPTIONAL)


class SOAP_HeaderFault(xsd.ComplexType):
    message = xsd.Attribute(xsd.QName)
    part = xsd.Attribute(xsd.NMTOKEN)
    use = xsd.Attribute(xsd.String(enumeration=['encoded', 'literal']))
    namespace = xsd.Attribute(xsd.AnyURI, use=xsd.Use.OPTIONAL)
    encodingStyle = xsd.Attribute(xsd.AnyURI, use=xsd.Use.OPTIONAL)


class SOAP_Header(xsd.ComplexType):
    message = xsd.Attribute(xsd.QName)
    part = xsd.Attribute(xsd.NMTOKEN)
    use = xsd.Attribute(xsd.String(enumeration=['encoded', 'literal']))
    namespace = xsd.Attribute(xsd.AnyURI, use=xsd.Use.OPTIONAL)
    encodingStyle = xsd.Attribute(xsd.AnyURI, use=xsd.Use.OPTIONAL)
    headerfaults = xsd.ListElement(SOAP_HeaderFault, 'headerfault', minOccurs=0, namespace=ns.wsdl_soap)


class SOAP_Body(xsd.ComplexType):
    ELEMENT_FORM_DEFAULT = xsd.ElementFormDefault.QUALIFIED
    parts = xsd.Attribute(xsd.NMTOKENS, use=xsd.Use.OPTIONAL)
    use = xsd.Attribute(xsd.String(enumeration=['encoded', 'literal']))
    namespace = xsd.Attribute(xsd.AnyURI, use=xsd.Use.OPTIONAL)
    encodingStyle = xsd.Attribute(xsd.AnyURI, use=xsd.Use.OPTIONAL)


class SOAP_Fault(xsd.ComplexType):
    ELEMENT_FORM_DEFAULT = xsd.ElementFormDefault.QUALIFIED
    name = xsd.Attribute(xsd.NMTOKEN)
    use = xsd.Attribute(xsd.String(enumeration=['encoded', 'literal']))
    namespace = xsd.Attribute(xsd.AnyURI, use=xsd.Use.OPTIONAL)
    encodingStyle = xsd.Attribute(xsd.AnyURI, use=xsd.Use.OPTIONAL)


class SOAP_Address(xsd.ComplexType):
    ELEMENT_FORM_DEFAULT = xsd.ElementFormDefault.QUALIFIED
    location = xsd.Attribute(xsd.AnyURI)


# WSDL 1.1 SOAP 1.1


class Types(xsd.ComplexType):
    schemas = xsd.ListElement(xsdspec.Schema, 'schema', namespace=xsdspec.XSD_NAMESPACE)
    documentation = xsd.Element(xsd.String, minOccurs=0)


class Part(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    element = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    type = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)


class Message(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    parts = xsd.ListElement(Part, tagname='part', minOccurs=0)
    documentation = xsd.Element(xsd.String, minOccurs=0)

    # FIXME: Remove this artificial restriction on the number of parts?!
    @property
    def part(self):
        if len(self.parts) != 1:
            raise ValueError('expected exactly one part', self.name, self.parts)
        return self.parts[0]


class Import(xsd.ComplexType):
    namespace = xsd.Attribute(xsd.String)
    location = xsd.Attribute(xsd.String)


class Input(xsd.ComplexType):
    name = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)      # See note #1.
    message = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)   # See note #2.
    documentation = xsd.Element(xsd.String, minOccurs=0)

    # Extensibility Elements:
    body = xsd.Element(SOAP_Body, namespace=ns.wsdl_soap)
    headers = xsd.ListElement(SOAP_Header, 'header', minOccurs=0, namespace=ns.wsdl_soap)


class Output(xsd.ComplexType):
    name = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)      # See note #1.
    message = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)   # See note #2.
    documentation = xsd.Element(xsd.String, minOccurs=0)

    # Extensibility Elements:
    body = xsd.Element(SOAP_Body, namespace=ns.wsdl_soap)
    headers = xsd.ListElement(SOAP_Header, 'header', minOccurs=0, namespace=ns.wsdl_soap)


class Fault(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    message = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)   # See note #2.
    documentation = xsd.Element(xsd.String, minOccurs=0)

    # Extensibility Elements:
    fault = xsd.Element(SOAP_Fault, namespace=ns.wsdl_soap)


class Operation(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    input = xsd.Element(Input, minOccurs=0)
    output = xsd.Element(Output, minOccurs=0)
    faults = xsd.ListElement(Fault, 'fault', minOccurs=0)
    documentation = xsd.Element(xsd.String, minOccurs=0)

    # Extensibility Elements:
    operation = xsd.Element(SOAP_Operation, minOccurs=0, namespace=ns.wsdl_soap)


class PortType(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    operations = xsd.ListElement(Operation, 'operation', minOccurs=0)
    documentation = xsd.Element(xsd.String, minOccurs=0)


class Binding(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    type = xsd.Attribute(xsd.String)
    operations = xsd.ListElement(Operation, 'operation', minOccurs=0)
    documentation = xsd.Element(xsd.String, minOccurs=0)

    # Extensibility Elements:
    binding = xsd.Element(SOAP_Binding, namespace=ns.wsdl_soap)


class Port(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    binding = xsd.Attribute(xsd.String)
    documentation = xsd.Element(xsd.String, minOccurs=0)

    # Extensibility Elements:
    address = xsd.Element(SOAP_Address, namespace=ns.wsdl_soap)


class Service(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    ports = xsd.ListElement(Port, 'port', minOccurs=0)
    documentation = xsd.Element(xsd.String, minOccurs=0)


class Definitions(xsd.ComplexType):
    name = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    targetNamespace = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    imports = xsd.ListElement(Import, 'import', minOccurs=0)
    types = xsd.Element(Types, minOccurs=0)
    messages = xsd.ListElement(Message, 'message', minOccurs=0)
    portTypes = xsd.ListElement(PortType, 'portType', minOccurs=0)
    bindings = xsd.ListElement(Binding, 'binding', minOccurs=0)
    services = xsd.ListElement(Service, 'service', minOccurs=0)
    documentation = xsd.Element(xsd.String, minOccurs=0)


SCHEMA = xsd.Schema(
    targetNamespace=ns.wsdl,
    elementFormDefault=xsd.ElementFormDefault.QUALIFIED,
    simpleTypes=[],
    attributeGroups=[],
    groups=[],
    complexTypes=[Types, Part, Message, Input, Output, Fault, Operation,
                  PortType, Binding, Port, Service, Import, Definitions],
    elements={},
)
