#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import logging
import sys
import textwrap

from datetime import datetime
from jinja2 import Environment, PackageLoader
from lxml import etree
import six

from .soap import SOAP_HTTP_Transport, SOAPVersion
from .utils import (
    capitalize,
    find_xsd_namespaces,
    get_get_type,
    open_document,
    remove_namespace,
    url_component,
    url_regex,
    url_template,
    use,
)
from .wsdl import get_wsdl_classes, get_by_name
from .xsd2py import schema_to_py, schema_name


TEMPLATE_PACKAGE = 'soapfish.templates'


logger = logging.getLogger('soapfish')


# --- Helpers -----------------------------------------------------------------
def get_rendering_environment():
    pkg = TEMPLATE_PACKAGE.split('.')
    env = Environment(
        extensions=['jinja2.ext.loopcontrols'],
        loader=PackageLoader(*pkg),
    )
    env.filters['capitalize'] = capitalize
    env.filters['remove_namespace'] = remove_namespace
    env.filters['url_component'] = url_component
    env.filters['url_regex'] = url_regex
    env.filters['url_template'] = url_template
    env.filters['use'] = use
    env.globals['SOAPTransport'] = SOAP_HTTP_Transport
    env.globals['get_by_name'] = get_by_name
    env.globals['schema_name'] = schema_name
    env.globals['generation_dt'] = datetime.now()
    return env


def generate_code_from_wsdl(xml, target, use_wsa=False, encoding='utf8'):
    env = get_rendering_environment()
    xmlelement = etree.fromstring(xml)
    XSD_NAMESPACE = find_xsd_namespaces(xmlelement.nsmap)
    env.filters['type'] = get_get_type(XSD_NAMESPACE)
    soap_version = SOAPVersion.get_version_from_xml(xmlelement)
    logger.info('Detect version %s', soap_version.NAME)

    wsdl = get_wsdl_classes(soap_version.BINDING_NAMESPACE)
    definitions = wsdl.Definitions.parse_xmlelement(xmlelement)
    schema = definitions.types.schema
    xsd_namespace = find_xsd_namespaces(xmlelement.nsmap)
    schemaxml = schema_to_py(schema, xsd_namespace,
                             parent_namespace=definitions.targetNamespace)

    tpl = env.get_template('wsdl')
    return tpl.render(
        soap_version=soap_version,
        definitions=definitions,
        schema=schemaxml,
        is_server=bool(target == 'server'),
        use_wsa=use_wsa,
    ).encode(encoding)


# --- Program -----------------------------------------------------------------
def parse_arguments():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            Generates Python code from a WSDL document.

            Code can be generated for a simple HTTP client or a server running
            the Django web framework.
        '''))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--client', help='Generate code for a client.', action='store_true')
    group.add_argument('-s', '--server', help='Generate code for a server.', action='store_true')
    parser.add_argument('-w', '--use-wsa', help='Use ws-addressing', action='store_true')
    parser.add_argument('wsdl', help='The path to a WSDL document.')
    return parser.parse_args()


def main():
    opt = parse_arguments()
    xml = open_document(opt.wsdl)
    target = 'server' if opt.server else 'client'
    logger.info('Generating %s code for WSDL document \'%s\'...' % (target, opt.wsdl))
    code = generate_code_from_wsdl(xml, target, opt.use_wsa)
    if six.PY3:
        sys.stdout.buffer.write(code)
    else:
        print(code)


if __name__ == '__main__':

    main()
