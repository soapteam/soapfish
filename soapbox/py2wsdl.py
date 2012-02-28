import sys
import imp
import xsd
from wsdl import get_wsdl_classes
from lxml import etree
from py2xsd import generate_xsdspec
from utils import uncapitalize
from soap import SOAP_HTTP_Transport

def build_service(wsdl,definitions, service):
    wsdl_service = wsdl.Service()
    wsdl_service.name = service.name

    wsdl_port = wsdl.Port()
    wsdl_port.name = service.name+"Port"
    wsdl_port.binding = "tns:" + service.name+"Binding"
    wsdl_port.address = wsdl.SOAP_Address(location=service.location)

    wsdl_service.ports.append(wsdl_port)
    definitions.services.append(wsdl_service)

def build_bindings(wsdl,definitions, service):
    binding = wsdl.Binding()
    binding.name = service.name +"Binding"
    binding.type = "tns:" + service.name + "PortType"
    binding.binding = wsdl.SOAP_Binding()
    binding.binding.style = "document"
    binding.binding.transport = SOAP_HTTP_Transport

    for method in service.methods:
        operation = wsdl.Operation()
        operation.name = method.operationName
        operation.operation = wsdl.SOAP_Operation()
        operation.operation.soapAction = method.soapAction
        operation.input = wsdl.Input(body=wsdl.SOAP_Body(use="literal"))
        operation.output = wsdl.Input(body=wsdl.SOAP_Body(use="literal"))
        operation.operation.style = method.style
        binding.operations.append(operation)

    definitions.bindings.append(binding)


def build_portTypes(wsdl,definitions, service):
    portType = wsdl.PortType()
    portType.name = service.name + "PortType"
    for method in service.methods:
        operation = wsdl.Operation()
        operation.name = method.operationName
        operation.input = wsdl.Input(message="tns:" +method.operationName+"Input")
        operation.output = wsdl.Input(message="tns:" +method.operationName+"Output")
        portType.operations.append(operation)

    definitions.portTypes.append(portType)

def build_messages(wsdl,definitions, service):
    for method in service.methods:
        inputMessage = wsdl.Message(name=method.operationName+"Input")
        inputMessage.part = wsdl.Part()
        inputMessage.part.name = "body"
        if isinstance(method.input, str):
            inputMessage.part.element = "sns:"+method.input
        else:
            inputMessage.part.type = "sns:"+uncapitalize(method.input.__name__)
        definitions.messages.append(inputMessage)

        outputMessage = wsdl.Message(name=method.operationName+"Output")
        outputMessage.part = wsdl.Part()
        outputMessage.part.name = "body"
        if isinstance(method.output, str):
            outputMessage.part.element = "sns:"+method.output
        else:
            outputMessage.part.type = "sns:"+uncapitalize(method.output.__name__)
        definitions.messages.append(outputMessage)

def build_types(wsdl,definitions, schema):
    xsd_schema = generate_xsdspec(schema)
    definitions.types = wsdl.Types(schema=xsd_schema)



def generate_wsdl(service):
    wsdl = get_wsdl_classes(service.version.BINDING_NAMESPACE)
    definitions = wsdl.Definitions(targetNamespace=service.targetNamespace)
    build_types(wsdl,definitions, service.schema)
    build_service(wsdl,definitions, service)
    build_bindings(wsdl,definitions, service)
    build_portTypes(wsdl,definitions, service)
    build_messages(wsdl,definitions, service)

    xmlelement = etree.Element("{http://schemas.xmlsoap.org/wsdl/}definitions",
                               nsmap = {"xsd" : "http://www.w3.org/2001/XMLSchema",
                                        "wsdl" : "http://schemas.xmlsoap.org/wsdl/",
                                        "soap" : service.version.BINDING_NAMESPACE,
                                        "sns" : service.schema.targetNamespace,
                                        "tns" : service.targetNamespace})
    definitions.render(xmlelement, definitions,
                       namespace="http://schemas.xmlsoap.org/wsdl/",
                       elementFormDefault=xsd.ElementFormDefault.QUALIFIED)
    return etree.tostring(xmlelement, pretty_print=True)


def main():
    if len(sys.argv) != 2:
        print "use: py2wsdl <path to python file>"
        return
    path = sys.argv[1]
    globals = imp.load_source("", path)
    service = getattr(globals,"SERVICE")
    print generate_wsdl(service)

if __name__ == "__main__":
    main()




