#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################

'''
'''

################################################################################
# Imports


import argparse
import hashlib
import httplib2
import keyword
import textwrap

from jinja2 import Environment, PackageLoader
from lxml import etree

from .xsdspec import Schema
from .utils import (
    classyfiy,
    find_xsd_namepsace,
    get_get_type,
    open_document,
    removens,
    use,
)


################################################################################
# Constants


TEMPLATE_PACKAGE = 'soapbox.templates'


################################################################################
# Helpers


def get_rendering_environment():
    '''
    '''
    pkg = TEMPLATE_PACKAGE.split('.')
    env = Environment(
        extensions=['jinja2.ext.loopcontrols'],
        loader=PackageLoader(*pkg),
    )
    env.filters['class'] = classyfiy
    env.filters['removens'] = removens
    env.filters['use'] = use
    env.globals['keywords'] = keyword.kwlist
    env.globals['resolve_import'] = resolve_import
    env.globals['schema_name'] = schema_name
    return env


def resolve_import(xsdimport, known_namespaces):
    '''
    '''
    xml = open_document(xsdimport.schemaLocation)
    xmlelement = etree.fromstring(xml)
    return generate_code_from_xsd(xmlelement, known_namespaces, xsdimport.schemaLocation)


def schema_name(namespace):
    '''
    '''
    return hashlib.sha512(namespace).hexdigest()[0:5]


def generate_code_from_xsd(xmlelement, known_namespaces=None, location=None):
    '''
    '''
    if known_namespaces is None:
        known_namespaces = []
    xsd_namespace = find_xsd_namepsace(xmlelement.nsmap)

    schema = Schema.parse_xmlelement(xmlelement)

    # Skip if this schema has already been included:
    if schema.targetNamespace in known_namespaces:
        return ''

    return schema_to_py(schema, xsd_namespace, known_namespaces, location)


def schema_to_py(schema, xsd_namespace, known_namespaces=None, location=None):
    '''
    '''
    if known_namespaces is None:
        known_namespaces = []
    known_namespaces.append(schema.targetNamespace)

    env = get_rendering_environment()
    env.filters['type'] = get_get_type(xsd_namespace)
    env.globals['known_namespaces'] = known_namespaces
    env.globals['location'] = location

    tpl = env.get_template('xsd')
    return tpl.render(schema=schema)


################################################################################
# Program


def parse_arguments():
    '''
    '''
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            Generates Python code from an XSD document.
        '''))
    parser.add_argument('xsd', help='The path to an XSD document.')
    return parser.parse_args()


def main():
    '''
    '''
    opt = parse_arguments()

    xml = open_document(opt.xsd)
    xmlelement = etree.fromstring(xml)
    print textwrap.dedent('''\
    from soapbox import xsd
    from soapbox.xsd import UNBOUNDED
    ''')
    print generate_code_from_xsd(xmlelement)


if __name__ == '__main__':

    main()


################################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
