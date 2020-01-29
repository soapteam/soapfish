from . import namespaces as ns, wsdl11, xsd

# FIXME: With the current implementation of schema we cannot share classes
#        between different schema so we duplicate classes from soapfish.wsdl11


class SOAP_Binding(wsdl11.SOAP_Binding):
    pass


class SOAP_Operation(wsdl11.SOAP_Operation):
    soapActionRequired = xsd.Attribute(xsd.Boolean, use=xsd.Use.OPTIONAL)


class SOAP_HeaderFault(wsdl11.SOAP_HeaderFault):
    pass


class SOAP_Header(wsdl11.SOAP_Header):
    headerfaults = xsd.ListElement(SOAP_HeaderFault, 'headerfault', minOccurs=0, namespace=ns.wsdl_soap12)


class SOAP_Body(wsdl11.SOAP_Body):
    pass


class SOAP_Fault(wsdl11.SOAP_Fault):
    pass


class SOAP_Address(wsdl11.SOAP_Address):
    pass


# WSDL 1.1 SOAP 1.2 classes


class Types(wsdl11.Types):
    pass


class Part(wsdl11.Part):
    pass


class Message(wsdl11.Message):
    parts = xsd.ListElement(Part, tagname='part', minOccurs=0)


class Import(wsdl11.Import):
    pass


# WSDL 1.1 SOAP 1.2 classes


class Input(wsdl11.Input):
    # Extensibility Elements:
    body = xsd.Element(SOAP_Body, namespace=ns.wsdl_soap12)
    headers = xsd.ListElement(SOAP_Header, 'header', minOccurs=0, namespace=ns.wsdl_soap12)


class Output(wsdl11.Output):
    # Extensibility Elements:
    body = xsd.Element(SOAP_Body, namespace=ns.wsdl_soap12)
    headers = xsd.ListElement(SOAP_Header, 'header', minOccurs=0, namespace=ns.wsdl_soap12)


class Fault(wsdl11.Fault):
    # Extensibility Elements:
    fault = xsd.Element(SOAP_Fault, namespace=ns.wsdl_soap12)


class Operation(wsdl11.Operation):
    input = xsd.Element(Input, minOccurs=0)
    output = xsd.Element(Output, minOccurs=0)
    faults = xsd.ListElement(Fault, 'fault', minOccurs=0)

    # Extensibility Elements:
    operation = xsd.Element(SOAP_Operation, minOccurs=0, namespace=ns.wsdl_soap12)


class PortType(wsdl11.PortType):
    operations = xsd.ListElement(Operation, 'operation', minOccurs=0)


class Binding(wsdl11.Binding):
    operations = xsd.ListElement(Operation, 'operation', minOccurs=0)

    # Extensibility Elements:
    binding = xsd.Element(SOAP_Binding, namespace=ns.wsdl_soap12)


class Port(wsdl11.Port):
    # Extensibility Elements:
    address = xsd.Element(SOAP_Address, namespace=ns.wsdl_soap12)


class Service(wsdl11.Service):
    ports = xsd.ListElement(Port, 'port', minOccurs=0)


class Definitions(wsdl11.Definitions):
    imports = xsd.ListElement(Import, 'import', minOccurs=0)
    types = xsd.Element(Types, minOccurs=0)
    messages = xsd.ListElement(Message, 'message', minOccurs=0)
    portTypes = xsd.ListElement(PortType, 'portType', minOccurs=0)
    bindings = xsd.ListElement(Binding, 'binding', minOccurs=0)
    services = xsd.ListElement(Service, 'service', minOccurs=0)


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
