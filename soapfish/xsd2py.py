#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import hashlib
import keyword
import logging
import os
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


def resolve_import(xsdimport, known_files, parent_namespace, cwd):
    location = os.path.join(cwd, xsdimport.schemaLocation)
    cwd = os.path.dirname(location)
    logger.info('Generating code for XSD import \'%s\'...' % location)
    xml = open_document(location)
    xmlelement = etree.fromstring(xml)
    return generate_code_from_xsd(xmlelement, known_files, location,
                                  parent_namespace, encoding=None, cwd=cwd)


def schema_name(schema, location=None):
    if not location:
        try:
            location = schema.schemaLocation
        except AttributeError:
            location = schema.targetNamespace

    try:
        location = location.encode()
    except UnicodeEncodeError:
        pass
    # we don't have any cryptographic requirements here and md5 is faster than
    # sha512 so there is no harm using an outdated algorithm.
    return hashlib.md5(location).hexdigest()[0:5]


def generate_code_from_xsd(xmlelement, known_files=None, location=None,
                           parent_namespace=None, encoding='utf8', cwd=None):
    if known_files is None:
        known_files = []
    xsd_namespace = find_xsd_namespaces(xmlelement.nsmap)

    schema = Schema.parse_xmlelement(xmlelement)

    # Skip if this schema has already been included:
    if schema.targetNamespace in known_files:
        return ''

    schema_code = schema_to_py(schema, xsd_namespace, known_files,
                               location, cwd=cwd)
    if encoding is None:
        return schema_code
    return schema_code.encode(encoding)


def schema_to_py(schema, xsd_namespace, known_files=None, location=None,
                 parent_namespace=None, cwd=None):
    if known_files is None:
        known_files = []
    if location:
        known_files.append(location)

    env = get_rendering_environment()
    env.filters['type'] = get_get_type(xsd_namespace)
    env.globals['known_files'] = known_files
    env.globals['location'] = location

    tpl = env.get_template('xsd')

    if schema.targetNamespace is None:
        schema.targetNamespace = parent_namespace

    return tpl.render(schema=schema, cwd=cwd)


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
