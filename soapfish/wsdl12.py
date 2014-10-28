# -*- coding: utf-8 -*-

from . import xsd
from . import wsdl11
from . import namespaces as ns


# With the current implementation of schema we cannot share classes
# between different schema so we duplicate wsdl11 classes

class SOAP_Binding(wsdl11.SOAP_Binding):
    pass


class SOAP_Operation(wsdl11.SOAP_Operation):
    pass


class SOAP_Header(wsdl11.SOAP_Header):
    pass


class SOAP_Body(wsdl11.SOAP_Body):
    pass


class SOAP_Address(wsdl11.SOAP_Address):
    pass


class Types(wsdl11.Types):
    pass


class Part(wsdl11.Part):
    pass


class Message(wsdl11.Message):
    pass

# WSDL 1.1 SOAP 1.2 classes

class Input(wsdl11.Input):
    body = xsd.Element(SOAP_Body, namespace=ns.wsdl_soap12, minOccurs=0)
    headers = xsd.ListElement(SOAP_Header, 'header', minOccurs=0)


class Operation(wsdl11.Operation):
    operation = xsd.Element(SOAP_Operation, namespace=ns.wsdl_soap12)
    input = xsd.Element(Input)
    output = xsd.Element(Input)
    body = xsd.Element(SOAP_Body, namespace=ns.wsdl_soap12)
    binding = xsd.Element('soapfish.wsdl12.Binding')
    definition = xsd.Element('soapfish.wsdl12.Definitions')


class PortType(wsdl11.PortType):
    operations = xsd.ListElement(Operation, 'operation')


class Binding(wsdl11.Binding):
    binding = xsd.Element(SOAP_Binding, namespace=ns.wsdl_soap12)
    operations = xsd.ListElement(Operation, 'operation')
    definition = xsd.Element('soapfish.wsdl12.Definitions')


class Port(wsdl11.Port):
    address = xsd.Element(SOAP_Address, namespace=ns.wsdl_soap12)


class Service(wsdl11.Service):
    ports = xsd.ListElement(Port, 'port')


class Definitions(wsdl11.Definitions):
    portTypes = xsd.ListElement(PortType, 'portType')
    bindings = xsd.ListElement(Binding, 'binding')
    services = xsd.ListElement(Service, 'service')


SCHEMA12 = xsd.Schema(
    targetNamespace=ns.wsdl,
    elementFormDefault=xsd.ElementFormDefault.QUALIFIED,
    simpleTypes=[],
    attributeGroups=[],
    groups=[],
    complexTypes=[Types, Part, Message, Input, Operation, PortType, Binding,
                  Port, Service, Definitions],
    elements={})
