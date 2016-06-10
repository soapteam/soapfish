#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import functools
import itertools
import logging
import os
import sys

import six
from lxml import etree

from . import xsdspec
from .utils import (
    find_xsd_namespaces,
    get_rendering_environment,
    open_document,
    resolve_location,
)

logger = logging.getLogger('soapfish')


# --- Helpers -----------------------------------------------------------------
def rewrite_paths(schema, cwd, base_path):
    """
    Rewrite include and import locations relative to base_path.

    This location is the unique identification for each file, they must match.
    """
    f = lambda x: os.path.relpath(os.path.normpath(os.path.join(cwd, x)), base_path)
    for i in itertools.chain(schema.includes, schema.imports):
        if i.schemaLocation is None or '://' in i.schemaLocation:
            continue
        i.schemaLocation = f(i.schemaLocation)


def resolve_import(i, known_files, parent_namespace, cwd, base_path):
    assert isinstance(i, (xsdspec.Import, xsdspec.Include))
    path, cwd, location = resolve_location(i.schemaLocation, base_path)
    tag = i.__class__.__name__.lower()
    logger.info('Generating code for xsd:%s=%s' % (tag, path))
    xml = open_document(path)

    return generate_code_from_xsd(xml, known_files, location,
                                  parent_namespace, encoding=None, cwd=cwd,
                                  base_path=base_path, standalone=False)


def generate_code_from_xsd(xml, known_files=None, location=None,
                           parent_namespace=None, encoding='utf8',
                           cwd=None, base_path=None, standalone=True):

    if isinstance(xml, six.binary_type):
        xml = etree.fromstring(xml)

    if cwd is None:
        cwd = six.moves.getcwd()

    if known_files is None:
        known_files = []

    xsd_namespaces = find_xsd_namespaces(xml)

    schema = xsdspec.Schema.parse_xmlelement(xml)

    # Skip if this file has already been included:
    if location and location in known_files:
        return ''

    code = schema_to_py(schema, xsd_namespaces, known_files,
                        location, cwd=cwd, base_path=base_path,
                        standalone=standalone)

    return code.encode(encoding) if encoding else code


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

    schema.complexTypes.sort(key=functools.cmp_to_key(_cmp))


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


def main(argv=None):
    stdin = getattr(sys.stdin, 'buffer', sys.stdin)
    stdout = getattr(sys.stdout, 'buffer', sys.stdin)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Generates Python code from an XSD document.',
    )
    parser.add_argument('xsd', help='Input path to an XSD document.')
    parser.add_argument('output', help='Output path for Python code.', nargs='?',
                        type=argparse.FileType('wb'), default=stdout)
    opt = parser.parse_args(sys.argv[1:] if argv is None else argv)

    logger.info('Generating code for XSD document: %s' % opt.xsd)
    xml = stdin.read() if opt.xsd == '-' else open_document(opt.xsd)
    cwd = os.path.dirname(os.path.abspath(opt.xsd))
    code = generate_code_from_xsd(xml, encoding='utf-8', cwd=cwd)

    opt.output.write(code)

    return 0


if __name__ == '__main__':

    sys.exit(main())
