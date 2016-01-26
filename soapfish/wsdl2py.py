#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import logging
import os
import sys
import textwrap
from collections import deque

import six
from lxml import etree

from .soap import SOAPVersion
from .utils import (
    find_xsd_namespaces,
    get_rendering_environment,
    open_document,
    resolve_location,
)
from .wsdl import get_wsdl_classes
from .xsd2py import schema_to_py

logger = logging.getLogger('soapfish')


# --- Helpers -----------------------------------------------------------------
def reorder_schemas(schemas):
    schemas, targets, counter, x = [], set(), len(schemas), deque(schemas)
    while x and counter > 0:
        counter -= 1
        schema = x.popleft()
        ns = {i.namespace for i in schema.imports}
        if x and ns and ns - targets:
            x.append(schema)
        else:
            schemas.append(schema)
            targets.add(schema.targetNamespace)
    schemas.extend(x)  # always add remaining unorderable schemas...
    return schemas


def merge_imports(wsdl, definitions, xsd_namespaces, cwd=None, seen=None):

    def deduplicate(seq):
        seen = set()
        return [x for x in seq if x not in seen and not seen.add(x)]

    if seen is None:
        seen = set()

    for i in definitions.imports:
        path, cwd, location = resolve_location(i.location, cwd)

        if path in seen:
            continue

        seen.add(path)

        xml = open_document(path)
        xml = etree.fromstring(xml)

        xsd_namespaces.update(find_xsd_namespaces(xml))

        imported = wsdl.Definitions.parse_xmlelement(xml)

        if imported.imports:
            merge_imports(wsdl, imported, xsd_namespaces, cwd=cwd, seen=seen)

        if imported.types and imported.types.schemas:
            if not definitions.types:
                definitions.types = wsdl.Types()
            definitions.types.schemas = deduplicate(imported.types.schemas + definitions.types.schemas)

        definitions.services = deduplicate(imported.services + definitions.services)
        definitions.bindings = deduplicate(imported.bindings + definitions.bindings)
        definitions.messages = deduplicate(imported.messages + definitions.messages)
        definitions.portTypes = deduplicate(imported.portTypes + definitions.portTypes)


def generate_code_from_wsdl(xml, target, use_wsa=False, encoding='utf8', cwd=None):

    if isinstance(xml, six.string_types):
        xml = etree.fromstring(xml)

    if cwd is None:
        cwd = six.moves.getcwd()

    xsd_namespaces = find_xsd_namespaces(xml)

    soap_version = SOAPVersion.get_version_from_xml(xml)
    logger.info('Detected version of SOAP: %s', soap_version.NAME)

    wsdl = get_wsdl_classes(soap_version.BINDING_NAMESPACE)
    definitions = wsdl.Definitions.parse_xmlelement(xml)
    merge_imports(wsdl, definitions, xsd_namespaces, cwd=cwd)

    kw = {'cwd': cwd, 'parent_namespace': definitions.targetNamespace}
    schemas = reorder_schemas(definitions.types.schemas) if definitions.types else []
    schemas = ''.join(schema_to_py(schema, xsd_namespaces, **kw) for schema in schemas)

    env = get_rendering_environment(xsd_namespaces, module='soapfish.wsdl2py')
    tpl = env.get_template('wsdl')

    code = tpl.render(
        soap_version=soap_version,
        definitions=definitions,
        schemas=schemas,
        is_server=bool(target == 'server'),
        use_wsa=use_wsa,
    )

    return code.encode(encoding) if encoding else code


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

    target = 'server' if opt.server else 'client'
    logger.info('Generating %s code for WSDL document: %s' % (target, opt.wsdl))
    xml = open_document(opt.wsdl)
    cwd = os.path.dirname(os.path.abspath(opt.wsdl))
    code = generate_code_from_wsdl(xml, target, opt.use_wsa, cwd=cwd)
    # Ensure that we output generated code bytes as expected:
    print_ = print if six.PY2 else sys.stdout.buffer.write
    print_(code)


if __name__ == '__main__':

    main()
