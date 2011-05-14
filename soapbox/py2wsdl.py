import sys
import imp
import wsdl
from lxml import etree
from py2xsd import generate_xsdspec
from utils import uncapitalize

def build_service(definitions, service):
    wsdl_service = wsdl.Service()
    for method in service.methods:
        wsdl_port = wsdl.Port()
        wsdl_port.name = method.operationName+"Port"
        wsdl_port.binding = "tns:" + method.operationName+"Binding"
        wsdl_port.address = wsdl.SOAP_Address(location=service.location)
        wsdl_service.port = wsdl_port
    definitions.services.append(wsdl_service)
    
def build_bindings(definitions, service):
    for method in service.methods:
        binding = wsdl.Binding()
        binding.name = method.operationName +"Binding"
        binding.type = "tns:" + method.operationName + "PortType"
        binding.binding = wsdl.SOAP_Binding()
        binding.binding.style = "document"
        binding.binding.transport = "http://schemas.xmlsoap.org/soap/http"
        
        operation = wsdl.Operation()
        operation.name = method.operationName
        operation.operation = wsdl.SOAP_Operation()
        operation.operation.soapAction = method.soapAction
        operation.input = wsdl.Input(body=wsdl.SOAP_Body(use="literal"))
        operation.output = wsdl.Input(body=wsdl.SOAP_Body(use="literal"))
        binding.operation = operation
        
        definitions.bindings.append(binding)
        
        
def build_portTypes(definitions, service):
    for method in service.methods:
        portType = wsdl.PortType()
        portType.name = method.operationName + "PortType"
        operation = wsdl.Operation()
        operation.name = method.operationName
        operation.input = wsdl.Input(message="tns:" +method.operationName+"Input")
        operation.output = wsdl.Input(message="tns:" +method.operationName+"Output")
        portType.operation = operation
        
        definitions.portTypes.append(portType)
        
def build_messages(definitions, service):
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
        
def build_types(definitions, schema):
    xsd_schema = generate_xsdspec(schema)
    definitions.types = wsdl.Types(schema=xsd_schema)
        
        
        
def generate_wsdl(service):
    definitions = wsdl.Definitions(targetNamespace=service.targetNamespace)
    build_types(definitions, service.schema)
    build_service(definitions, service)
    build_bindings(definitions, service)
    build_portTypes(definitions, service)
    build_messages(definitions, service)
    
    xmlelement = etree.Element("{http://schemas.xmlsoap.org/wsdl/}definitions",
                               nsmap = {"xsd" : "http://www.w3.org/2001/XMLSchema",
                                        "wsdl" : "http://schemas.xmlsoap.org/wsdl/",
                                        "soap" : "http://schemas.xmlsoap.org/wsdl/soap/",
                                        "sns" : service.schema.targetNamespace,
                                        "tns" : service.targetNamespace})
    definitions.render(xmlelement, definitions, "http://schemas.xmlsoap.org/wsdl/")
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
    
    
    
    