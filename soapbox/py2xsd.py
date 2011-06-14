#This modules translates Python model code to xsdspec nodes that can be
#used to xsd generation.
import sys
import imp
from lxml import etree
import xsd
import xsdspec
from utils import uncapitalize

NUMERIC_TYPES = [xsd.Decimal, xsd.Integer, xsd.Int, xsd.Long]
def get_xsd_type(_type):
    """Check is basic type from XSD scope, else it must be user 
    defined type."""
    base_class = _type.__class__.__bases__[0]
    if base_class == xsd.SimpleType or _type.__class__  in NUMERIC_TYPES:
        return "xsd:" + uncapitalize(_type.__class__.__name__)
    else:
        return "sns:" + uncapitalize(_type.__class__.__name__)
    
def xsd_attribute(attribute):
    xsdattr = xsdspec.Attribute()
    xsdattr.name = attribute._name
    xsdattr.use = attribute.use
    xsdattr.type = get_xsd_type(attribute._type)
    return xsdattr

def create_xsd_element(element):
    xsd_element = xsdspec.Element()
    xsd_element.name = element._name
    if getattr(element,"nillable"):
        xsd_element.nillable = True
    if element._minOccurs == 0:
        xsd_element.minOccurs = 0
        
    # SimpleType defined in place.
    parent_type = element._type.__class__.__bases__[0]
    is_simple_type = False
    _type = element._type
    
    if hasattr(element._type, "enumeration") and element._type.enumeration\
    or hasattr(_type,"fractionDigits") and _type.fractionDigits\
    or hasattr(_type,"pattern") and _type.pattern\
    or hasattr(_type,"minInclusive") and _type.minInclusive\
    or hasattr(_type,"minExclusive") and _type.minExclusive\
    or hasattr(_type,"maxExclusive") and _type.maxExclusive\
    or hasattr(_type,"maxInclusive") and _type.maxInclusive\
    or hasattr(_type,"totalDigits") and _type.totalDigits:
        xsd_element.simpleType = xsdspec.SimpleType()
        xsd_element.simpleType.restriction = xsdspec.Restriction()
        xsd_element.simpleType.restriction.base = get_xsd_type(element._type)
        is_simple_type = True
        
    if hasattr(element._type, "enumeration") and element._type.enumeration\
    and parent_type == xsd.SimpleType:
        for value in element._type.enumeration:
            enum = xsdspec.Enumeration.create(value)
            xsd_element.simpleType.restriction.enumerations.append(enum)
    
    if hasattr(_type,"fractionDigits") and _type.fractionDigits:
        xsd_element.simpleType.restriction.fractionDigits = xsdspec.RestrictionValue(value=_type.fractionDigits)
        
    if hasattr(_type,"pattern") and _type.pattern:
        xsd_element.simpleType.restriction.pattern = xsdspec.RestrictionValue(value=_type.pattern)
        
    if hasattr(_type,"minInclusive") and _type.minInclusive:
        xsd_element.simpleType.restriction.minInclusive = xsdspec.RestrictionValue(value=_type.minInclusive)
        
    if hasattr(_type,"minExclusive") and _type.minExclusive:
        xsd_element.simpleType.restriction.minExclusive = xsdspec.RestrictionValue(value=_type.minExclusive)
        
    if hasattr(_type,"maxExclusive") and _type.maxExclusive:
        xsd_element.simpleType.restriction.maxExclusive = xsdspec.RestrictionValue(value=_type.maxExclusive)
        
    if hasattr(_type,"maxInclusive") and _type.maxInclusive:
        xsd_element.simpleType.restriction.maxInclusive = xsdspec.RestrictionValue(value=_type.maxInclusive)
        
    if hasattr(_type,"totalDigits") and _type.totalDigits:
        xsd_element.simpleType.restriction.totalDigits = xsdspec.RestrictionValue(value=_type.totalDigits)
    
    if not is_simple_type:
        xsd_element.type = get_xsd_type(element._type)
    return xsd_element

def xsd_complexType(complexType):
    xsd_ct = xsdspec.ComplexType()
    xsd_ct.name = uncapitalize(complexType.__name__)
    
    for attribute in complexType._meta.attributes:
        xsd_attr = xsd_attribute(attribute)
        xsd_ct.attributes.append(xsd_attr)
        
    #Elements can be wrapped with few type of containers:
    # sequence, all, choice or it can be a complexContent with 
    # extension or restriction. 
    if hasattr(complexType, "INDICATOR") and complexType.INDICATOR:
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
    xsd_simpleType = xsdspec.SimpleType()
    xsd_simpleType.name = st.__name__.lower()
    xsd_restriction = xsdspec.Restriction()
    xsd_restriction.base = get_xsd_type(st.__bases__[0]())
    if hasattr(st,"enumeration") and st.enumeration:
        for enum in st.enumeration:
            xsd_restriction.enumerations.append(xsdspec.Enumeration.create(enum))
    if hasattr(st,"fractionDigits") and st.fractionDigits:
        xsd_restriction.fractionDigits = xsdspec.RestrictionValue(value=st.fractionDigits)
    elif hasattr(st, "pattern") and st.pattern:
        xsd_restriction.pattern = st.pattern
    xsd_simpleType.restriction = xsd_restriction
    return xsd_simpleType

def generate_xsdspec(schema):
    xsd_schema = xsdspec.Schema()
    xsd_schema.targetNamespace = schema.targetNamespace
    for st in schema.simpleTypes:
        xsd_st = xsd_simpleType(st)
        xsd_schema.simpleTypes.append(xsd_st)
    for ct in schema.complexTypes:
        xsd_ct = xsd_complexType(ct)
        xsd_schema.complexTypes.append(xsd_ct)
    generate_elements(xsd_schema, schema)
    return xsd_schema

def generate_elements(xsd_schema, schema):
    for name, element in schema.elements.iteritems():
        xsd_element = xsdspec.Element()
        xsd_element.name = name
        xsd_element.type = get_xsd_type(element._type)
        xsd_schema.elements.append(xsd_element)
        
    
def generate_xsd(schema):
    xsd_schema = generate_xsdspec(schema)
    xmlelement = etree.Element("{http://www.w3.org/2001/XMLSchema}schema",
                               nsmap = {"xsd" : "http://www.w3.org/2001/XMLSchema",
                                        "sns" : schema.targetNamespace})
    xsd_schema.render(xmlelement, xsd_schema)
    return xmlelement
    

def main():
    import os
    if len(sys.argv) != 2:
        print "Use: py2xsd <path to pytho file>"
        return
    module = sys.argv[1]
    globals = imp.load_source("module.name", module)
    schema = getattr(globals,"Schema")
    schemaelement = generate_xsd(schema)
    print etree.tostring(schemaelement, pretty_print=True)
    
if __name__ == "__main__":
    main()
        

