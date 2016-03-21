# -*- coding: utf-8 -*-

from . import namespaces as ns, wsdl, xsd, xsdspec


# FIXME: With the current implementation of schema we cannot share classes
#        between different schema so we duplicate classes to soapfish.wsdl12

# Notes:
# ------
#
# 1. Only optional for <wsdl:operation> under <wsdl:portType>
# 2. Only required for <wsdl:operation> under <wsdl:portType>


class SOAP_Binding(xsd.ComplexType):
    ELEMENT_FORM_DEFAULT = xsd.ElementFormDefault.QUALIFIED
    style = xsd.Attribute(xsd.String)
    transport = xsd.Attribute(xsd.String)


class SOAP_Operation(xsd.ComplexType):
    ELEMENT_FORM_DEFAULT = xsd.ElementFormDefault.QUALIFIED
    soapAction = xsd.Attribute(xsd.String)
    style = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)


class SOAP_Header(xsd.ComplexType):
    message = xsd.Attribute(xsd.String)
    part = xsd.Attribute(xsd.String)
    use = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)


class SOAP_Body(xsd.ComplexType):
    ELEMENT_FORM_DEFAULT = xsd.ElementFormDefault.QUALIFIED
    use = xsd.Attribute(xsd.String)


class SOAP_Address(xsd.ComplexType):
    ELEMENT_FORM_DEFAULT = xsd.ElementFormDefault.QUALIFIED
    location = xsd.Attribute(xsd.String)


# WSDL 1.1 SOAP 1.1


class Types(xsd.ComplexType):
    schema = xsd.Element(xsdspec.Schema, namespace=xsdspec.XSD_NAMESPACE)
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


class Input(xsd.ComplexType):
    name = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)      # See note #1.
    message = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)   # See note #2.
    documentation = xsd.Element(xsd.String, minOccurs=0)

    # Extensibility Elements:
    body = xsd.Element(SOAP_Body, namespace=ns.wsdl_soap, minOccurs=0)
    headers = xsd.ListElement(SOAP_Header, 'header', minOccurs=0)


class Output(xsd.ComplexType):
    name = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)      # See note #1.
    message = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)   # See note #2.
    documentation = xsd.Element(xsd.String, minOccurs=0)

    # Extensibility Elements:
    body = xsd.Element(SOAP_Body, namespace=ns.wsdl_soap, minOccurs=0)
    headers = xsd.ListElement(SOAP_Header, 'header', minOccurs=0)


class Operation(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    input = xsd.Element(Input, minOccurs=0)
    output = xsd.Element(Output, minOccurs=0)
    documentation = xsd.Element(xsd.String, minOccurs=0)

    # Extensibility Elements:
    body = xsd.Element(SOAP_Body, namespace=ns.wsdl_soap)
    operation = xsd.Element(SOAP_Operation, namespace=ns.wsdl_soap)


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
    complexTypes=[Types, Part, Message, Input, Output, Operation, PortType,
                  Binding, Port, Service, Definitions],
    elements={},
)
