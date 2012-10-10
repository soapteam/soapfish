# -*- coding: utf-8 -*-
################################################################################

'''
'''

################################################################################
# Imports


from . import xsd


################################################################################
# Constants


XSD_NAMESPACE = 'http://www.w3.org/2001/XMLSchema'


################################################################################
# Classes


class Enumeration(xsd.ComplexType):
    '''
    '''
    value = xsd.Attribute(xsd.String)

    @classmethod
    def create(cls, value):
        '''
        '''
        enum = Enumeration()
        enum.value = value
        return enum


class Pattern(xsd.ComplexType):
    '''
    '''
    NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
    value = xsd.Attribute(xsd.String)


class RestrictionValue(xsd.ComplexType):
    '''
    '''
    NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
    value = xsd.Attribute(xsd.String)


class Restriction(xsd.ComplexType):
    '''
    '''
    NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
    base = xsd.Attribute(xsd.String)
    enumerations = xsd.ListElement(Enumeration, 'enumeration')
    pattern = xsd.Element(Pattern)
    minInclusive = xsd.Element(RestrictionValue)
    minExclusive = xsd.Element(RestrictionValue)
    maxExclusive = xsd.Element(RestrictionValue)
    maxInclusive = xsd.Element(RestrictionValue)
    fractionDigits = xsd.Element(RestrictionValue)
    totalDigits = xsd.Element(RestrictionValue)

    def to_python(self):
        enum_values = map(lambda e: '\'%s\'' % e.value, self.enumerations)
        return '[%s]' % ','.join(enum_values)


class Union(xsd.ComplexType):
    '''
    '''
    NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
    memberTypes = xsd.Attribute(xsd.String)


class List(xsd.ComplexType):
    '''
    '''
    NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
    pass


class SimpleType(xsd.ComplexType):
    '''
    '''
    NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
    name = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    restriction = xsd.Element(Restriction, minOccurs=0)
    union = xsd.Element(Union, minOccurs=0)
    list = xsd.Element(List, minOccurs=0)


class Element(xsd.ComplexType):
    '''
    '''
    NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
    name = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    type = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    ref = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    minOccurs = xsd.Attribute(xsd.Integer, use=xsd.Use.OPTIONAL)
    maxOccurs = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    nillable = xsd.Attribute(xsd.Boolean, use=xsd.Use.OPTIONAL)
    simpleType = xsd.Element(SimpleType, minOccurs=0)
    complexType = xsd.Element('XSDComplexType')


class Sequence(xsd.ComplexType):
    '''
    '''
    NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
    elements = xsd.ListElement(Element, 'element')


class Attribute(xsd.ComplexType):
    '''
    '''
    NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
    name = xsd.Attribute(xsd.String)
    ref = xsd.Attribute(xsd.String)
    type = xsd.Attribute(xsd.String)
    use = xsd.Attribute(xsd.String)


class AttributeGroup(xsd.ComplexType):
    '''
    '''
    NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
    name = xsd.Attribute(xsd.String)
    attributes = xsd.ListElement(Attribute, 'attribute')


class AttributeGroupReference(xsd.ComplexType):
    '''
    '''
    NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
    ref = xsd.Attribute(xsd.String)

    def to_python(self):
        typename = get_type(self.ref)
        data = {'name': typename.lower(), 'type': typename}
        return '''    %(name)s = xsd.Ref(%(type)s)\n''' % data


class Extension(xsd.ComplexType):
    '''
    '''
    NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
    base = xsd.Attribute(xsd.String)
    sequence = xsd.Element(Sequence)
    attributes = xsd.ListElement(Attribute, 'attribute')
    attributeGroups = xsd.ListElement(AttributeGroupReference, 'attributeGroup')


class ComplexContent(xsd.ComplexType):
    '''
    '''
    NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
    mixed = xsd.Attribute(xsd.Boolean)
    extension = xsd.Element(Extension)
    restriction = xsd.Element(Extension)


class XSDComplexType(xsd.ComplexType):
    '''
    '''
    NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
    name = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    sequence = xsd.Element(Sequence)
    choice = xsd.Element(Sequence)
    all = xsd.Element(Sequence)
    complexContent = xsd.Element(ComplexContent)
    attributes = xsd.ListElement(Attribute, 'attribute')
    attributeGroups = xsd.ListElement(AttributeGroupReference, 'attributeGroup')


class Group(xsd.ComplexType):
    '''
    '''
    NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
    name = xsd.Attribute(xsd.String)
    sequence = xsd.Element(Sequence)


class Import(xsd.ComplexType):
    '''
    '''
    schemaLocation = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    namespace = xsd.Attribute(xsd.String)


class Schema(xsd.ComplexType):
    '''
    '''
    NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
    targetNamespace = xsd.Attribute(xsd.String)
    elementFormDefault = xsd.Attribute(
        xsd.String(enumeration=['qualified', 'unqualified']),
        use=xsd.Use.OPTIONAL, default='unqualified',
    )
    imports = xsd.ListElement(Import, 'import')
    simpleTypes = xsd.ListElement(SimpleType, 'simpleType')
    groups = xsd.ListElement(Group, 'group')
    attributeGroups = xsd.ListElement(AttributeGroup, 'attributeGroup')
    complexTypes = xsd.ListElement(XSDComplexType, 'complexType')
    elements = xsd.ListElement(Element, 'element')


SCHEMA = xsd.Schema(
    targetNamespace='http://www.w3.org/2001/XMLSchema',
    elementFormDefault=xsd.ElementFormDefault.QUALIFIED,
    simpleTypes=[],
    attributeGroups=[],
    groups=[],
    complexTypes=[Enumeration, Pattern, Union, RestrictionValue, Restriction, List,
                  SimpleType, Element, Sequence, Attribute, AttributeGroup,
                  AttributeGroupReference, Extension, ComplexContent,
                  XSDComplexType, Group, Schema],
    elements={},
)


################################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
