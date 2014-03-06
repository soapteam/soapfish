# -*- coding: utf-8 -*-

from . import xsd, xsdspec
from . import wsdl
from . import namespaces as ns


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


class Types(xsd.ComplexType):
    schema = xsd.Element(xsdspec.Schema, namespace=xsdspec.XSD_NAMESPACE)


class Part(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    element = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    type = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)


class Message(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    parts = xsd.ListElement(Part, tagname='part', minOccurs=1)

    @property
    def part(self):
        if len(self.parts) != 1:
            raise ValueError('expected exactly one part', self.name, self.parts)
        return self.parts[0]


# WSDL 1.1 SOAP 1.1

class Input(xsd.ComplexType):
    message = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    body = xsd.Element(SOAP_Body, namespace=ns.wsdl_soap, minOccurs=0)
    headers = xsd.ListElement(SOAP_Header, 'header', minOccurs=0)


class Operation(xsd.ComplexType):
    operation = xsd.Element(SOAP_Operation, namespace=ns.wsdl_soap)
    name = xsd.Attribute(xsd.String)
    input = xsd.Element(Input)
    output = xsd.Element(Input)
    body = xsd.Element(SOAP_Body, namespace=ns.wsdl_soap)
    binding = xsd.Element('soapbox.wsdl11.Binding')
    definition = xsd.Element('soapbox.wsdl11.Definitions')

    def __init__(self, **kwargs):
        super(Operation, self).__init__(**kwargs)
        self.binding = None
        self.definition = None

    def render(self, *args, **kwargs):
        self.binding = None
        self.definition = None
        super(Operation, self).render(*args, **kwargs)

    def set_definition(self, definition):
        self.definition = definition

    def set_binding(self, binding):
        self.binding = binding

    def _get_Message(self, direction):
        portType = self.binding.getPortType()
        portTypeOperation = wsdl.get_by_name(portType.operations, self.name)
        messageName = getattr(portTypeOperation, direction).message
        return wsdl.get_by_name(self.definition.messages, messageName)

    def get_InputMessage(self):
        return self._get_Message('input')

    def get_OutputMessage(self):
        return self._get_Message('output')

    def get_InputMessageHeaders(self):
        operation = wsdl.get_by_name(self.binding.operations, self.name)
        return self._get_parts(operation.input.headers)

    def get_OutputMessage(self):
        portType = self.binding.getPortType()
        portTypeOperation = wsdl.get_by_name(portType.operations, self.name)
        messageName = portTypeOperation.output.message
        return wsdl.get_by_name(self.definition.messages, messageName)

    def get_OutputMessageHeaders(self):
        operation = wsdl.get_by_name(self.binding.operations, self.name)
        return self._get_parts(operation.output.headers)

    def _get_parts(self, references):
        parts = []
        for ref in references:
            message = wsdl.get_by_name(self.definition.messages, ref.message)
            parts.append(wsdl.get_by_name(message.parts, ref.part))
        return parts



class PortType(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    operations = xsd.ListElement(Operation, 'operation')


class Binding(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    type = xsd.Attribute(xsd.String)
    binding = xsd.Element(SOAP_Binding, namespace=ns.wsdl_soap)
    operations = xsd.ListElement(Operation, 'operation')
    definition = xsd.Element('soapbox.wsdl11.Definitions')

    def render(self, *args, **kwargs):
        self.definition = None
        super(Binding, self).render(*args, **kwargs)

    def __init__(self, **kwargs):
        super(Binding, self).__init__(**kwargs)
        self.definition = None

    def set_definition(self, definition):
        self.definition = definition

    def feedback_Operations(self):
        for operation in self.operations:
            operation.set_binding(self)

    def getPortType(self):
        return wsdl.get_by_name(self.definition.portTypes, self.type)


class Port(xsd.ComplexType):
    name = xsd.Attribute(xsd.String)
    binding = xsd.Attribute(xsd.String)
    address = xsd.Element(SOAP_Address, namespace=ns.wsdl_soap)


class Service(xsd.ComplexType):
    name = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    documentation = xsd.Element(xsd.String)
    ports = xsd.ListElement(Port, 'port')


class Definitions(xsd.ComplexType):
    targetNamespace = xsd.Attribute(xsd.String)
    types = xsd.Element(Types)
    messages = xsd.ListElement(Message, 'message')
    portTypes = xsd.ListElement(PortType, 'portType')
    bindings = xsd.ListElement(Binding, 'binding')
    services = xsd.ListElement(Service, 'service')


SCHEMA = xsd.Schema(
    targetNamespace=ns.wsdl,
    elementFormDefault=xsd.ElementFormDefault.QUALIFIED,
    simpleTypes=[],
    attributeGroups=[],
    groups=[],
    complexTypes=[Types, Part, Message, Input, Operation, PortType, Binding,
                  Port, Service, Definitions],
    elements={})
