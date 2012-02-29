#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################

'''
'''

################################################################################
# Imports


import argparse
import imp
import inspect
import textwrap

from lxml import etree

from . import xsd, xsdspec
from .utils import uncapitalize


################################################################################
# Constants


NUMERIC_TYPES = [xsd.Decimal, xsd.Integer, xsd.Int, xsd.Long, xsd.Short,
        xsd.UnsignedByte, xsd.UnsignedInt, xsd.UnsignedLong, xsd.UnsignedShort,
        xsd.Double, xsd.Float, xsd.Byte]

STRING_TYPES = [xsd.QName, xsd.AnyURI, xsd.Base64Binary, xsd.QName,
        xsd.AnyType, xsd.Duration]

ALL_TYPES = NUMERIC_TYPES + STRING_TYPES


################################################################################
# Helpers


def get_xsd_type(_type):
    '''
    Check is basic type from XSD scope, else it must be user defined type.
    '''
    base_class = _type.__class__.__bases__[0]
    if base_class == xsd.SimpleType or _type.__class__  in ALL_TYPES:
        return 'xsd:' + uncapitalize(_type.__class__.__name__)
    else:
        return 'sns:' + uncapitalize(_type.__class__.__name__)


def xsd_attribute(attribute):
    '''
    '''
    xsdattr = xsdspec.Attribute()
    xsdattr.name = attribute._name
    xsdattr.use = attribute.use
    xsdattr.type = get_xsd_type(attribute._type)
    return xsdattr


def create_xsd_element(element):
    '''
    '''
    xsd_element = xsdspec.Element()
    xsd_element.name = element.tagname if element.tagname else element._name
    xsd_element.nillable = element.nillable
    xsd_element.minOccurs = element._minOccurs
    if hasattr(element, '_maxOccurs'):
        xsd_element.maxOccurs = element._maxOccurs

    # SimpleType defined in place.
    parent_type = element._type.__class__.__bases__[0]
    _type = element._type

    if not inspect.isclass(element._passed_type):
        xsd_element.simpleType = xsdspec.SimpleType()
        xsd_element.simpleType.restriction = xsdspec.Restriction()
        xsd_element.simpleType.restriction.base = get_xsd_type(element._type)

        if hasattr(element._type, 'enumeration') and element._type.enumeration\
        and parent_type == xsd.SimpleType:
            for value in element._type.enumeration:
                enum = xsdspec.Enumeration.create(value)
                xsd_element.simpleType.restriction.enumerations.append(enum)

        if hasattr(_type, 'fractionDigits') and _type.fractionDigits:
            xsd_element.simpleType.restriction.fractionDigits = xsdspec.RestrictionValue(value=str(_type.fractionDigits))

        if hasattr(_type, 'pattern') and _type.pattern:
            xsd_element.simpleType.restriction.pattern = xsdspec.RestrictionValue(value=str(_type.pattern))

        if hasattr(_type, 'minInclusive') and _type.minInclusive:
            xsd_element.simpleType.restriction.minInclusive = xsdspec.RestrictionValue(value=str(_type.minInclusive))

        if hasattr(_type, 'minExclusive') and _type.minExclusive:
            xsd_element.simpleType.restriction.minExclusive = xsdspec.RestrictionValue(value=str(_type.minExclusive))

        if hasattr(_type, 'maxExclusive') and _type.maxExclusive:
            xsd_element.simpleType.restriction.maxExclusive = xsdspec.RestrictionValue(value=str(_type.maxExclusive))

        if hasattr(_type, 'maxInclusive') and _type.maxInclusive:
            xsd_element.simpleType.restriction.maxInclusive = xsdspec.RestrictionValue(value=str(_type.maxInclusive))

        if hasattr(_type, 'totalDigits') and _type.totalDigits:
            xsd_element.simpleType.restriction.totalDigits = xsdspec.RestrictionValue(value=str(_type.totalDigits))
    else:
        xsd_element.type = get_xsd_type(element._type)
    return xsd_element


def xsd_complexType(complexType, named=True):
    '''
    '''
    xsd_ct = xsdspec.XSDComplexType()
    if named:
        xsd_ct.name = uncapitalize(complexType.__name__)

    for attribute in complexType._meta.attributes:
        xsd_attr = xsd_attribute(attribute)
        xsd_ct.attributes.append(xsd_attr)

    # Elements can be wrapped with few type of containers:
    # sequence, all, choice or it can be a complexContent with
    # extension or restriction.
    if hasattr(complexType, 'INDICATOR') and complexType.INDICATOR:
        xsd_sequence = xsdspec.Sequence()
        xsd_ct.sequence = xsd_sequence
        container = xsd_sequence
    else:
        container = xsd_ct

    for element in complexType._meta.fields:
        xsd_element = create_xsd_element(element)
        container.elements.append(xsd_element)
    return xsd_ct


def xsd_simpleType(st):
    '''
    '''
    xsd_simpleType = xsdspec.SimpleType()
    xsd_simpleType.name = uncapitalize(st.__name__)
    xsd_restriction = xsdspec.Restriction()
    xsd_restriction.base = get_xsd_type(st.__bases__[0]())
    if hasattr(st, 'enumeration') and st.enumeration:
        for enum in st.enumeration:
            xsd_restriction.enumerations.append(xsdspec.Enumeration.create(enum))
    if hasattr(st, 'fractionDigits') and st.fractionDigits:
        xsd_restriction.fractionDigits = xsdspec.RestrictionValue(value=st.fractionDigits)
    elif hasattr(st, 'pattern') and st.pattern:
        xsd_restriction.pattern = xsdspec.Pattern(value=st.pattern)
    xsd_simpleType.restriction = xsd_restriction
    return xsd_simpleType


def build_imports(xsd_schema, imports):
    '''
    '''
    counter = 0
    if imports:
        for _import in imports:
            xsd_import = xsdspec.Import()
            xsd_import.namespace = _import.targetNamespace
            if _import.location:
                xsd_import.schemaLocation = _import.location
            xsd_schema.imports.append(xsd_import)
            counter += 1


def generate_xsdspec(schema):
    '''
    '''
    xsd_schema = xsdspec.Schema()
    xsd_schema.targetNamespace = schema.targetNamespace

    build_imports(xsd_schema, schema.imports)
    for st in schema.simpleTypes:
        xsd_st = xsd_simpleType(st)
        xsd_schema.simpleTypes.append(xsd_st)

    for ct in schema.complexTypes:
        xsd_ct = xsd_complexType(ct)
        xsd_schema.complexTypes.append(xsd_ct)

    generate_elements(xsd_schema, schema)
    return xsd_schema


def generate_elements(xsd_schema, schema):
    '''
    '''
    for name, element in schema.elements.iteritems():
        xsd_element = xsdspec.Element()
        xsd_element.name = name
        if isinstance(element._passed_type, basestring) or inspect.isclass(element._passed_type):
            xsd_element.type = get_xsd_type(element._type)
        else:
            xsd_element.complexType = xsd_complexType(element._type.__class__, named=False)
        xsd_schema.elements.append(xsd_element)


def generate_xsd(schema):
    '''
    '''
    xsd_schema = generate_xsdspec(schema)

    xmlelement = etree.Element(
        '{http://www.w3.org/2001/XMLSchema}schema',
        nsmap={
            'sns': schema.targetNamespace,
            'xsd': xsdspec.XSD_NAMESPACE,
        },
    )

    xsd_schema.render(xmlelement,
                      xsd_schema,
                      namespace=xsdspec.XSD_NAMESPACE,
                      elementFormDefault=xsd.ElementFormDefault.QUALIFIED)
    return xmlelement


################################################################################
# Program


def parse_arguments():
    '''
    '''
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            Generates an XSD document from a Python module.
        '''))
    parser.add_argument('module', help='The path to a python module.')
    return parser.parse_args()


def main():
    '''
    '''
    opt = parse_arguments()

    module = imp.load_source('module.name', opt.module)
    schema = getattr(module, 'Schema')
    tree = generate_xsd(schema)
    print etree.tostring(tree, pretty_print=True)


if __name__ == '__main__':

    main()


################################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
