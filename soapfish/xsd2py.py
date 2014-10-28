#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import hashlib
import keyword
import logging
import sys
import textwrap

from jinja2 import Environment, PackageLoader
from lxml import etree
import six

from . import xsd
from .xsdspec import Schema
from .utils import (
    capitalize,
    find_xsd_namespaces,
    get_get_type,
    open_document,
    remove_namespace,
    url_template,
    use,
)


TEMPLATE_PACKAGE = 'soapfish.templates'


logger = logging.getLogger('soapfish')


# --- Helpers -----------------------------------------------------------------
def get_rendering_environment():
    pkg = TEMPLATE_PACKAGE.split('.')
    env = Environment(
        extensions=['jinja2.ext.loopcontrols',
                    'jinja2.ext.do'],
        loader=PackageLoader(*pkg),
    )
    env.filters['capitalize'] = capitalize
    env.filters['remove_namespace'] = remove_namespace
    env.filters['url_template'] = url_template
    env.filters['use'] = use
    env.filters['max_occurs_to_code'] = lambda x: 'xsd.UNBOUNDED' if x is xsd.UNBOUNDED else str(x)

    env.globals['keywords'] = keyword.kwlist
    env.globals['resolve_import'] = resolve_import
    env.globals['schema_name'] = schema_name
    return env


def resolve_import(xsdimport, known_namespaces):
    logger.info('Generating code for XSD import \'%s\'...' % xsdimport.schemaLocation)
    xml = open_document(xsdimport.schemaLocation)
    xmlelement = etree.fromstring(xml)
    return generate_code_from_xsd(xmlelement, known_namespaces, xsdimport.schemaLocation, encoding=None)


def schema_name(namespace):
    # we don't have any cryptographic requirements here and md5 is faster than
    # sha512 so there is no harm using an outdated algorithm.
    return hashlib.md5(namespace.encode()).hexdigest()[0:5]


def generate_code_from_xsd(xmlelement, known_namespaces=None, location=None, encoding='utf8'):
    if known_namespaces is None:
        known_namespaces = []
    xsd_namespace = find_xsd_namespaces(xmlelement.nsmap)

    schema = Schema.parse_xmlelement(xmlelement)

    # Skip if this schema has already been included:
    if schema.targetNamespace in known_namespaces:
        return ''

    schema_code = schema_to_py(schema, xsd_namespace, known_namespaces, location)
    if encoding is None:
        return schema_code
    return schema_code.encode(encoding)


def schema_to_py(schema, xsd_namespace, known_namespaces=None, location=None):
    if known_namespaces is None:
        known_namespaces = []
    known_namespaces.append(schema.targetNamespace)

    env = get_rendering_environment()
    env.filters['type'] = get_get_type(xsd_namespace)
    env.globals['known_namespaces'] = known_namespaces
    env.globals['location'] = location

    tpl = env.get_template('xsd')
    return tpl.render(schema=schema)


# --- Program -----------------------------------------------------------------
def parse_arguments():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            Generates Python code from an XSD document.
        '''))
    parser.add_argument('xsd', help='The path to an XSD document.')
    return parser.parse_args()


def main():
    opt = parse_arguments()

    logger.info('Generating code for XSD document \'%s\'...' % opt.xsd)
    xml = open_document(opt.xsd)
    xmlelement = etree.fromstring(xml)
    print(textwrap.dedent('''\
        # -*- coding: utf-8 -*-

        from soapfish import xsd
        from soapfish.xsd import UNBOUNDED
    '''))
    code = generate_code_from_xsd(xmlelement, encoding='utf-8')
    # In Python 3 encoding a string returns bytes so we have to write the
    # generated code to sys.stdout.buffer instead of sys.stdout.
    # We should not depend on Python 3's "auto-conversion to console charset"
    # because this might fail for file redirections and cron jobs which might
    # use pure ASCII.
    if six.PY3:
        sys.stdout.buffer.write(code)
    else:
        print(code)


if __name__ == '__main__':

    main()
