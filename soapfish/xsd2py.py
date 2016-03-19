#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import functools
import itertools
import logging
import os
import sys
import textwrap

import six
from lxml import etree

from .utils import (
    find_xsd_namespaces,
    get_rendering_environment,
    open_document,
)
from .xsdspec import Schema

logger = logging.getLogger('soapfish')


# --- Helpers -----------------------------------------------------------------
def rewrite_paths(schema, cwd, base_path):
    """
    Rewrite include and import locations relative to base_path.

    This location is the unique identification for each file, they must match.
    """
    f = lambda x: os.path.relpath(os.path.normpath(os.path.join(cwd, x.schemaLocation)), base_path)
    for i in itertools.chain(schema.includes, schema.imports):
        if i.schemaLocation is None:
            continue
        i.schemaLocation = f(i)


def resolve_import(xsdimport, known_files, parent_namespace, cwd, base_path):
    location = os.path.join(base_path, xsdimport.schemaLocation)
    cwd = os.path.dirname(location)
    logger.info('Generating code for XSD import \'%s\'...' % location)
    xml = open_document(location)
    xmlelement = etree.fromstring(xml)

    location = os.path.relpath(location, base_path)
    return generate_code_from_xsd(xmlelement, known_files, location,
                                  parent_namespace, encoding=None,
                                  cwd=cwd, base_path=base_path)


def generate_code_from_xsd(xmlelement, known_files=None, location=None,
                           parent_namespace=None, encoding='utf8',
                           cwd=None, base_path=None):
    if known_files is None:
        known_files = []
    xsd_namespaces = find_xsd_namespaces(xmlelement.nsmap)

    schema = Schema.parse_xmlelement(xmlelement)

    # Skip if this file has already been included:
    if location and location in known_files:
        return ''

    schema_code = schema_to_py(schema, xsd_namespaces, known_files,
                               location, cwd=cwd, base_path=base_path,
                               standalone=True)
    if encoding is None:
        return schema_code
    return schema_code.encode(encoding)


def _reorder_complexTypes(schema):
    """
    Reorder complexTypes to render base extension/restriction elements
    render before the children.
    """
    weights = {}
    for n, complex_type in enumerate(schema.complexTypes):
        content = complex_type.complexContent
        if content:
            extension = content.extension
            restriction = content.restriction
            if extension:
                base = extension.base
            elif restriction:
                base = restriction.base
        else:
            base = ''

        weights[complex_type.name] = (n, base)

    def _cmp(a, b):
        a = getattr(a, 'name', a)
        b = getattr(b, 'name', b)

        w_a, base_a = weights[a]
        w_b, base_b = weights[b]
        # a and b are not extension/restriction
        if not base_a and not base_b:
            return w_a - w_b
        is_extension = lambda obj, base: (obj == base)
        has_namespace = lambda base: (':' in base)
        # a is a extension/restriction of b: a > b
        if is_extension(b, base_a) or has_namespace(base_a):
            return 1
        # b is a extension/restriction of a: a < b
        elif is_extension(a, base_b) or has_namespace(base_b):
            return -1
        # inconclusive, do the same test with their bases
        return _cmp(base_a or a, base_b or b)

    if hasattr(functools, 'cmp_to_key'):
        sort_param = {'key': functools.cmp_to_key(_cmp)}
    else:
        # Python 2.6/3.0/3.1
        sort_param = {'cmp': _cmp}
    schema.complexTypes.sort(**sort_param)


def schema_to_py(schema, xsd_namespaces, known_files=None, location=None,
                 parent_namespace=None, cwd=None, base_path=None,
                 standalone=False):
    if base_path is None:
        base_path = cwd
    if base_path:
        rewrite_paths(schema, cwd, base_path)

    _reorder_complexTypes(schema)

    if known_files is None:
        known_files = []
    if location:
        known_files.append(location)

    if schema.targetNamespace is None:
        schema.targetNamespace = parent_namespace

    env = get_rendering_environment(xsd_namespaces, module='soapfish.xsd2py')
    env.globals.update(
        known_files=known_files,
        location=location,
        resolve_import=resolve_import,
    )
    if not standalone:
        del env.globals['preamble']
    tpl = env.get_template('xsd')

    return tpl.render(schema=schema, cwd=cwd, base_path=base_path)


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
