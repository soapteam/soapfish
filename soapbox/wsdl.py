# -*- coding: utf-8 -*-

from . import xsd, xsdspec


# --- Functions ---------------------------------------------------------------
def get_by_name(_list, fullname):
    name = fullname.split(':')[-1]
    for item in _list:
        if item.name == name:
            return item
    raise ValueError("Item '%s' not found in list:%s" % (name, _list))


def get_wsdl_classes(soap_namespace):

    class SOAP_Binding(xsd.ComplexType):
        ELEMENT_FORM_DEFAULT = xsd.ElementFormDefault.QUALIFIED
        style = xsd.Attribute(xsd.String)
        transport = xsd.Attribute(xsd.String)

    class SOAP_Operation(xsd.ComplexType):
        ELEMENT_FORM_DEFAULT = xsd.ElementFormDefault.QUALIFIED
        soapAction = xsd.Attribute(xsd.String)
        style = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)

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
        part = xsd.Element(Part)

    class Input(xsd.ComplexType):
        message = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
        body = xsd.Element(SOAP_Body, namespace=soap_namespace, minOccurs=0)

    class Operation(xsd.ComplexType):
        operation = xsd.Element(SOAP_Operation, namespace=soap_namespace)
        name = xsd.Attribute(xsd.String)
        input = xsd.Element(Input)
        output = xsd.Element(Input)
        body = xsd.Element(SOAP_Body, namespace=soap_namespace)
        binding = xsd.Element('Binding')
        definition = xsd.Element('Definitions')

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

        def get_InputMessage(self):
            portType = self.binding.getPortType()
            portTypeOperation = get_by_name(portType.operations, self.name)
            messageName = portTypeOperation.input.message
            return get_by_name(self.definition.messages, messageName)

        def get_OutputMessage(self):
            portType = self.binding.getPortType()
            portTypeOperation = get_by_name(portType.operations, self.name)
            messageName = portTypeOperation.output.message
            return get_by_name(self.definition.messages, messageName)

    class PortType(xsd.ComplexType):
        name = xsd.Attribute(xsd.String)
        operations = xsd.ListElement(Operation, 'operation')

    class Binding(xsd.ComplexType):
        name = xsd.Attribute(xsd.String)
        type = xsd.Attribute(xsd.String)
        binding = xsd.Element(SOAP_Binding, namespace=soap_namespace)
        operations = xsd.ListElement(Operation, 'operation')
        definition = xsd.Element('Definitions')

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
            return get_by_name(self.definition.portTypes, self.type)

    class Port(xsd.ComplexType):
        name = xsd.Attribute(xsd.String)
        binding = xsd.Attribute(xsd.String)
        address = xsd.Element(SOAP_Address, namespace=soap_namespace)

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
        targetNamespace='http://schemas.xmlsoap.org/wsdl/',
        elementFormDefault=xsd.ElementFormDefault.QUALIFIED,
        simpleTypes=[],
        attributeGroups=[],
        groups=[],
        complexTypes=[Types, Part, Message, Input, Operation, PortType, Binding,
                      Port, Service, Definitions],
        elements={})

    class wsdl(object):

        def __init__(self):
            self.Binding = Binding
            self.Definitions = Definitions
            self.Input = Input
            self.Message = Message
            self.Operation = Operation
            self.Part = Part
            self.Port = Port
            self.PortType = PortType
            self.SOAP_Address = SOAP_Address
            self.SOAP_Binding = SOAP_Binding
            self.SOAP_Body = SOAP_Body
            self.SOAP_Operation = SOAP_Operation
            self.Service = Service
            self.Types = Types

    return wsdl()
