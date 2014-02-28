# -*- coding: utf-8 -*-

from . import xsd, xsdspec
from . import wsdl, wsdl11


wsdl11_ns = 'http://schemas.xmlsoap.org/wsdl/'
wsdl11_soap12_ns = 'http://schemas.xmlsoap.org/wsdl/soap12/'


# With the current implementation of schema we cannot share classes
# between different schema so we duplicate wsdl11 classes

class SOAP_Binding(wsdl11.SOAP_Binding):
    pass


class SOAP_Operation(wsdl11.SOAP_Operation):
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
    body = xsd.Element(SOAP_Body, namespace=wsdl11_soap12_ns, minOccurs=0)


class Operation(wsdl11.Operation):
    operation = xsd.Element(SOAP_Operation, namespace=wsdl11_soap12_ns)
    input = xsd.Element(Input)
    output = xsd.Element(Input)
    body = xsd.Element(SOAP_Body, namespace=wsdl11_soap12_ns)
    binding = xsd.Element('Binding')
    definition = xsd.Element('Definitions')


class PortType(wsdl11.PortType):
    operations = xsd.ListElement(Operation, 'operation')


class Binding(wsdl11.Binding):
    binding = xsd.Element(SOAP_Binding, namespace=wsdl11_soap12_ns)
    operations = xsd.ListElement(Operation, 'operation')
    definition = xsd.Element('Definitions')


class Port(wsdl11.Port):
    address = xsd.Element(SOAP_Address, namespace=wsdl11_soap12_ns)


class Service(wsdl11.Service):
    ports = xsd.ListElement(Port, 'port')


class Definitions(wsdl11.Definitions):
    portTypes = xsd.ListElement(PortType, 'portType')
    bindings = xsd.ListElement(Binding, 'binding')
    services = xsd.ListElement(Service, 'service')


SCHEMA12 = xsd.Schema(
    targetNamespace=wsdl11_ns,
    elementFormDefault=xsd.ElementFormDefault.QUALIFIED,
    simpleTypes=[],
    attributeGroups=[],
    groups=[],
    complexTypes=[Types, Part, Message, Input, Operation, PortType, Binding,
                  Port, Service, Definitions],
    elements={})
