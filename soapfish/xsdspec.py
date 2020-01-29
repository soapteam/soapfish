from . import namespaces as ns, xsd

XSD_NAMESPACE = ns.xsd


class Enumeration(xsd.ComplexType):
    value = xsd.Attribute(xsd.String)

    @classmethod
    def create(cls, value):
        enum = Enumeration()
        enum.value = value
        return enum


class Pattern(xsd.ComplexType):
    NAMESPACE = ns.xsd
    value = xsd.Attribute(xsd.String)


class RestrictionValue(xsd.ComplexType):
    NAMESPACE = ns.xsd
    value = xsd.Attribute(xsd.String)

    def __repr__(self):
        return 'RestrictionValue<%r>' % self.value


class Restriction(xsd.ComplexType):
    NAMESPACE = ns.xsd
    base = xsd.Attribute(xsd.String)
    enumerations = xsd.ListElement(Enumeration, 'enumeration')
    pattern = xsd.Element(Pattern)
    minInclusive = xsd.Element(RestrictionValue)
    minExclusive = xsd.Element(RestrictionValue)
    maxExclusive = xsd.Element(RestrictionValue)
    maxInclusive = xsd.Element(RestrictionValue)
    fractionDigits = xsd.Element(RestrictionValue)
    totalDigits = xsd.Element(RestrictionValue)

    length = xsd.Element(RestrictionValue)
    minLength = xsd.Element(RestrictionValue)
    maxLength = xsd.Element(RestrictionValue)
    whiteSpace = xsd.Element(RestrictionValue)

    def to_python(self):
        return '[%s]' % ', '.join("'%s'" % e.value for e in self.enumerations)


class List(xsd.ComplexType):
    NAMESPACE = ns.xsd
    pass


class SimpleType(xsd.ComplexType):
    NAMESPACE = ns.xsd
    name = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    restriction = xsd.Element(Restriction, minOccurs=0)
    list = xsd.Element(List, minOccurs=0)


class Element(xsd.ComplexType):
    NAMESPACE = ns.xsd
    name = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    type = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    ref = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    minOccurs = xsd.Attribute(xsd.Integer, use=xsd.Use.OPTIONAL)
    maxOccurs = xsd.Attribute(xsd.MaxOccurs, use=xsd.Use.OPTIONAL)
    nillable = xsd.Attribute(xsd.Boolean, use=xsd.Use.OPTIONAL)
    substitutionGroup = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)  # FIXME: Should use xsd.List(xsd.QName)?
    simpleType = xsd.Element(SimpleType, minOccurs=0)
    complexType = xsd.Element('soapfish.xsdspec.XSDComplexType')


class Sequence(xsd.ComplexType):
    NAMESPACE = ns.xsd
    elements = xsd.ListElement(Element, 'element')


class Attribute(xsd.ComplexType):
    NAMESPACE = ns.xsd
    name = xsd.Attribute(xsd.String)
    ref = xsd.Attribute(xsd.String)
    type = xsd.Attribute(xsd.String)
    use = xsd.Attribute(xsd.String)
    simpleType = xsd.Element(SimpleType, minOccurs=0)


class AttributeGroup(xsd.ComplexType):
    NAMESPACE = ns.xsd
    name = xsd.Attribute(xsd.String)
    attributes = xsd.ListElement(Attribute, 'attribute')


class AttributeGroupReference(xsd.ComplexType):
    NAMESPACE = ns.xsd
    ref = xsd.Attribute(xsd.String)

    def to_python(self):
        from .utils import get_type
        typename = get_type(self.ref)
        data = {'name': typename.lower(), 'type': typename}
        return '''    %(name)s = xsd.Ref(%(type)s)\n''' % data


class Extension(xsd.ComplexType):
    NAMESPACE = ns.xsd
    base = xsd.Attribute(xsd.String)
    sequence = xsd.Element(Sequence)
    attributes = xsd.ListElement(Attribute, 'attribute')
    attributeGroups = xsd.ListElement(AttributeGroupReference, 'attributeGroup')


class ComplexContent(xsd.ComplexType):
    NAMESPACE = ns.xsd
    mixed = xsd.Attribute(xsd.Boolean)
    extension = xsd.Element(Extension)
    restriction = xsd.Element(Extension)


class XSDComplexType(xsd.ComplexType):
    NAMESPACE = ns.xsd
    name = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    sequence = xsd.Element(Sequence)
    choice = xsd.Element(Sequence)
    all = xsd.Element(Sequence)
    complexContent = xsd.Element(ComplexContent)
    attributes = xsd.ListElement(Attribute, 'attribute')
    attributeGroups = xsd.ListElement(AttributeGroupReference, 'attributeGroup')


class Group(xsd.ComplexType):
    NAMESPACE = ns.xsd
    name = xsd.Attribute(xsd.String)
    sequence = xsd.Element(Sequence)


class Import(xsd.ComplexType):
    schemaLocation = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    namespace = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)


class Include(xsd.ComplexType):
    schemaLocation = xsd.Attribute(xsd.String)


class Schema(xsd.ComplexType):
    NAMESPACE = ns.xsd
    targetNamespace = xsd.Attribute(xsd.String)
    elementFormDefault = xsd.Attribute(
        xsd.String(enumeration=['qualified', 'unqualified']),
        use=xsd.Use.OPTIONAL, default='unqualified',
    )
    imports = xsd.ListElement(Import, 'import')
    includes = xsd.ListElement(Include, 'include')
    simpleTypes = xsd.ListElement(SimpleType, 'simpleType')
    groups = xsd.ListElement(Group, 'group')
    attributeGroups = xsd.ListElement(AttributeGroup, 'attributeGroup')
    complexTypes = xsd.ListElement(XSDComplexType, 'complexType')
    elements = xsd.ListElement(Element, 'element')

    def get_element_by_name(self, name):
        # FIXME: Handle imported and included schemas.
        for element in self.elements:
            if name == element.name:
                return element
        else:
            return None


SCHEMA = xsd.Schema(
    targetNamespace=ns.xsd,
    elementFormDefault=xsd.ElementFormDefault.QUALIFIED,
    simpleTypes=[],
    attributeGroups=[],
    groups=[],
    complexTypes=[Enumeration, Pattern, RestrictionValue, Restriction, List,
                  SimpleType, Element, Sequence, Attribute, AttributeGroup,
                  AttributeGroupReference, Extension, ComplexContent,
                  XSDComplexType, Group, Schema],
    elements={},
)
