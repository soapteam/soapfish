#!/usr/bin/env python

import argparse
import logging
import sys
from importlib.machinery import SourceFileLoader

from lxml import etree

from . import namespaces as ns, xsd
from .py2xsd import generate_xsdspec
from .soap import SOAP_HTTP_Transport
from .utils import uncapitalize
from .wsdl import get_wsdl_classes

logger = logging.getLogger('soapfish')


# --- Helpers -----------------------------------------------------------------
def build_service(wsdl, definitions, service):
    wsdl_port = wsdl.Port()
    wsdl_port.name = service.name + 'Port'
    wsdl_port.binding = 'tns:' + service.name + 'Binding'
    wsdl_port.address = wsdl.SOAP_Address(location=service.location)

    wsdl_service = wsdl.Service()
    wsdl_service.name = service.name
    wsdl_service.ports.append(wsdl_port)

    definitions.services.append(wsdl_service)


def build_bindings(wsdl, definitions, service):
    binding = wsdl.Binding()
    binding.name = service.name + 'Binding'
    binding.type = 'tns:' + service.name + 'PortType'
    binding.binding = wsdl.SOAP_Binding()
    binding.binding.style = 'document'
    binding.binding.transport = SOAP_HTTP_Transport

    for method in service.methods:
        operation = wsdl.Operation()
        operation.name = method.operationName
        operation.operation = wsdl.SOAP_Operation()
        operation.operation.soapAction = method.soapAction
        operation.input = wsdl.Input(body=wsdl.SOAP_Body(use='literal'))
        operation.output = wsdl.Output(body=wsdl.SOAP_Body(use='literal'))
        operation.operation.style = method.style
        binding.operations.append(operation)

    definitions.bindings.append(binding)


def build_portTypes(wsdl, definitions, service):
    portType = wsdl.PortType()
    portType.name = service.name + 'PortType'

    for method in service.methods:
        operation = wsdl.Operation()
        operation.name = method.operationName
        operation.input = wsdl.Input(message='tns:' + method.operationName + 'Input')
        operation.output = wsdl.Output(message='tns:' + method.operationName + 'Output')
        portType.operations.append(operation)

    definitions.portTypes.append(portType)


def build_messages(wsdl, definitions, service):
    for method in service.methods:
        inputMessage = wsdl.Message(name=method.operationName + 'Input')
        part = wsdl.Part(name='body')
        if isinstance(method.input, str):
            part.element = 'sns:' + method.input
        else:
            part.type = 'sns:' + uncapitalize(method.input.__name__)
        inputMessage.parts = [part]
        definitions.messages.append(inputMessage)

        outputMessage = wsdl.Message(name=method.operationName + 'Output')
        part = wsdl.Part(name='body')
        if isinstance(method.output, str):
            part.element = 'sns:' + method.output
        else:
            part.type = 'sns:' + uncapitalize(method.output.__name__)
        outputMessage.parts = [part]
        definitions.messages.append(outputMessage)


def build_types(wsdl, definitions, service):
    schemas = [generate_xsdspec(schema) for schema in service.schemas]
    definitions.types = wsdl.Types(schemas=schemas)


def generate_wsdl(service):
    wsdl = get_wsdl_classes(service.version.BINDING_NAMESPACE)
    definitions = wsdl.Definitions(targetNamespace=service.targetNamespace)
    build_types(wsdl, definitions, service)
    build_service(wsdl, definitions, service)
    build_bindings(wsdl, definitions, service)
    build_portTypes(wsdl, definitions, service)
    build_messages(wsdl, definitions, service)

    xmlelement = etree.Element(
        '{%s}definitions' % ns.wsdl,
        nsmap={
            # FIXME: Look up properly if multiple schemas...
            'sns': service.schemas[0].targetNamespace,
            'soap': service.version.BINDING_NAMESPACE,
            'tns': service.targetNamespace,
            'wsdl': ns.wsdl,
            'xsd': ns.xsd,
        },
    )

    definitions.render(xmlelement,
                       definitions,
                       namespace=ns.wsdl,
                       elementFormDefault=xsd.ElementFormDefault.QUALIFIED)

    return xmlelement


# --- Program -----------------------------------------------------------------


def main(argv=None):
    stdout = getattr(sys.stdout, 'buffer', sys.stdout)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Generates a WSDL document from a Python module.',
    )
    parser.add_argument('module', help='The path to a python module.')
    parser.add_argument('output', help='Output path for WSDL document.',
                        nargs='?', type=argparse.FileType('wb'), default=stdout)
    opt = parser.parse_args(sys.argv[1:] if argv is None else argv)

    logger.info('Generating WSDL for Python module: %s', opt.module)

    module = SourceFileLoader('', opt.module).load_module()
    tree = generate_wsdl(module.SERVICE)

    opt.output.write(etree.tostring(tree, pretty_print=True))

    return 0


if __name__ == '__main__':

    sys.exit(main())
