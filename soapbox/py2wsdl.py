#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import imp
import logging
import textwrap
import six

from lxml import etree

from . import xsd
from .compat import NullHandler
from .py2xsd import generate_xsdspec
from .soap import SOAP_HTTP_Transport
from .utils import uncapitalize
from .wsdl import get_wsdl_classes

basestring = six.string_types

logger = logging.getLogger('soapbox')
logger.addHandler(NullHandler())


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
        operation.output = wsdl.Input(body=wsdl.SOAP_Body(use='literal'))
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
        operation.output = wsdl.Input(message='tns:' + method.operationName + 'Output')
        portType.operations.append(operation)

    definitions.portTypes.append(portType)


def build_messages(wsdl, definitions, service):
    for method in service.methods:
        inputMessage = wsdl.Message(name=method.operationName + 'Input')
        inputMessage.part = wsdl.Part()
        inputMessage.part.name = 'body'
        if isinstance(method.input, basestring):
            inputMessage.part.element = 'sns:' + method.input
        else:
            inputMessage.part.type = 'sns:' + uncapitalize(method.input.__name__)
        definitions.messages.append(inputMessage)

        outputMessage = wsdl.Message(name=method.operationName + 'Output')
        outputMessage.part = wsdl.Part()
        outputMessage.part.name = 'body'
        if isinstance(method.output, basestring):
            outputMessage.part.element = 'sns:' + method.output
        else:
            outputMessage.part.type = 'sns:' + uncapitalize(method.output.__name__)
        definitions.messages.append(outputMessage)


def build_types(wsdl, definitions, schema):
    xsd_schema = generate_xsdspec(schema)
    definitions.types = wsdl.Types(schema=xsd_schema)


def generate_wsdl(service):
    wsdl = get_wsdl_classes(service.version.BINDING_NAMESPACE)
    definitions = wsdl.Definitions(targetNamespace=service.targetNamespace)
    build_types(wsdl, definitions, service.schema)
    build_service(wsdl, definitions, service)
    build_bindings(wsdl, definitions, service)
    build_portTypes(wsdl, definitions, service)
    build_messages(wsdl, definitions, service)

    xmlelement = etree.Element(
        '{http://schemas.xmlsoap.org/wsdl/}definitions',
        nsmap={
            'sns': service.schema.targetNamespace,
            'soap': service.version.BINDING_NAMESPACE,
            'tns': service.targetNamespace,
            'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
            'xsd': 'http://www.w3.org/2001/XMLSchema',
        },
    )

    definitions.render(xmlelement,
                       definitions,
                       namespace='http://schemas.xmlsoap.org/wsdl/',
                       elementFormDefault=xsd.ElementFormDefault.QUALIFIED)

    return xmlelement


# --- Program -----------------------------------------------------------------
def parse_arguments():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            Generates a WSDL document from a Python module.
        '''))
    parser.add_argument('module', help='The path to a python module.')
    return parser.parse_args()


def main():
    opt = parse_arguments()

    logger.info('Generating WSDL for module \'%s\'...' % opt.module)
    module = imp.load_source('', opt.module)
    service = getattr(module, 'SERVICE')
    tree = generate_wsdl(service)
    print(etree.tostring(tree, pretty_print=True))


if __name__ == '__main__':

    main()
