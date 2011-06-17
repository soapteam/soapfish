from lxml import etree
from datetime import datetime
from copy import copy
import re
from utils import uncapitalize
#http://lxml.de/validation.html#xmlschema

#Design Decision Log:
#0. I have decided to not use dews/dexml approach to field description
# as it doesn't give good distinction between element and attribute.
# It is not a problem when parsing a XML, but it is quite important
# for rendering and XSD generation. The new syntax will look like:
# tail_number = xsd.Attribute(xsd.String)
# flight_number = xsd.Element(xsd.Interger)
# which makes this distinction clear.
# 
#1. render will take value/instance as parameter
# More obvious would be if render just rendered current object,
# but this approach doesn't work with Python simple types like string.
# Where you can not call "x".render() so type method render must
# take a value as a parameter, which may same odd for complex types.
#
#2. Due to render taking a value as parameter it could be implemented 
# as a static/class method, but it is not. 
# xsd.Element takes a class or an instance, but if class was passed
# it will create an instance - so parameterless constructor is required
# Reason for that is to keep API consistent. There are two syntaxes
# a) xsd.Element(xsd.String)
# b) xsd.Element(xsd.String(enumeration=["A","B"])
# Because instance if required in case b) creating it from class in case
# a) makes other methods independent from this two syntaxes.

NIL = object()

class TypeRegister(object):
    """Allows tracking user defined class and their names, to be able to resolve 
    string references e.g. a = xsd.Element("A"). Note that class names must be unique
    due to fact that search engine uses just class names."""
    def __init__(self):
        self.types = []
    
    def add_type(self, clazz):
        self.types.append(clazz)
    
    def find_type(self, typeid):
        for clazz in self.types:
            if clazz.__name__ == typeid:
                return clazz
    
USER_TYPE_REGISTER = TypeRegister()

UNBOUNDED = "unbounded"

class Use:
    OPTIONAL = "optional"
    REQUIRED = "required"
    PROHIBITED = "prohibited"
    
class Inheritance:
    RESTRICTION = "RESTRICTION"
    EXTENSION = "EXTENSION"
    
class ElementFormDefault:
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    
class Indicator(object):
    def __init__(self, fields):
        self.fields = fields
        
class Sequence(Indicator):
    pass

class Choice(Indicator):
    pass

class All(Indicator):
    pass


class Type_PythonType(type):
    def __new__(cls,name,bases,attrs):
        newcls = super(Type_PythonType,cls).__new__(cls,name,bases,attrs)
        USER_TYPE_REGISTER.add_type(newcls)
        return newcls
    
class Type(object):   
    """Abstract."""     
    __metaclass__ = Type_PythonType
    def accept(self, value):
        raise NotImplementedError
    
    def parse_xmlelement(self, xmlelement):
        raise NotImplementedError
    
    def parsexml(self, xml):
        raise NotImplementedError

    def rander(self, parent, value):
        raise NotImplementedError
    
    
class SimpleType(Type):
    """Defines an interface for simple types."""    
    def render(self, parent, value, namespace):
        parent.text = self.xmlvalue(value)
        
    def parse_xmlelement(self, xmlelement):
        return self.pythonvalue(xmlelement.text)
        
    def xmlvalue(self, value):
        raise NotImplementedError
    
    def pythonvalue(self, xmlavalue):
        raise NotImplementedError
    
        
class String(SimpleType):    
    enumeration = None#To be defined in child.
    def __init__(self, enumeration=None):
        if enumeration:
            self.enumeration = enumeration
        
    def accept(self,value):
        if value is None:
            return value
        if not isinstance(value,str):
            raise ValueError("Value '%s' for class '%s'." % (str(value),self.__class__.__name__))
        if self.enumeration:
            if value in self.enumeration:
                return value
            else:
                raise ValueError("Value '%s' not in list %s." % (str(value), self.enumeration))
        else:
            return value
        
    def xmlvalue(self, value):
        return value
    
    def pythonvalue(self, xmlvalue):
        return xmlvalue
        
class Boolean(SimpleType):
    def accept(self, value):
        if value in [True, False, None]:
            return value
        else:
            raise ValueError("Value '%s' for class '%s'." % (str(value),self.__class__.__name__))
        
    def xmlvalue(self, value):
        if value == True:
            return "true"
        elif value == False:
            return "false"
        elif value is None:
            return "nil"
        else:
            raise ValueError("Value '%s' for class '%s'." % (str(value),self.__class__.__name__))
        
    def pythonvalue(self,value):
        if value == 'false':
            return False
        elif value == 'true':
            return True
        elif value == 'nil' or value is None:
            return None
        else:
            raise ValueError("Boolean value error - %s" % value)
        
        
        
class DateTime(SimpleType):
    """Example text value: 2001-10-26T21:32:52"""
    FORMTA = "%Y-%m-%dT%H:%M:%S"            
    def accept(self, value):
        if value is None:
            return None
        elif isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            return datetime.strptime(value, self.FORMTA)
        raise ValueError("Incorrect type value '%s' for Datetime field." % value)
    
    def xmlvalue(self, value):
        if value is None:
            return "nil"
        else:
            return value.strftime(self.FORMTA)
        
    def pythonvalue(self, value):
        if value is None or value == 'nil':
            return None
        else:
            return datetime.strptime(value, self.FORMTA)
            
            
            
class Decimal(SimpleType):
    def __init__(self, enumeration = None, fractionDigits=None, maxExclusive=None, 
                 maxInclusive=None, minExclusive=None, minInclusive=None, 
                 pattern=None, totalDigits=None):
        self.enumeration = enumeration
        self.fractionDigits = fractionDigits
        self.maxExclusive = maxExclusive
        self.maxInclusive = maxInclusive
        self.minExclusive = minExclusive
        self.minInclusive = minInclusive
        self.pattern = pattern
        self.totalDigits = totalDigits
        
    def _check_restrictions(self, value):
        if self.enumeration is not None and value not in self.enumeration:
            raise ValueError("%s not in enumeration %s" % (value,self.enumeration))
        
        if self.fractionDigits is not None:
            strvalue = str(value)
            if self.fractionDigits == 0:
                if strvalue.find(".") != -1:
                    raise ValueError("Wrong fraction digits for value %s allowed %s" % (strvalue, self.fractionDigits))
            else:
                if strvalue.find(".") == -1:
                    raise ValueError("Wrong fraction digits for value %s allowed %s" % (strvalue, self.fractionDigits))
                fr = strvalue.split(".")[1]
                if len(fr) != self.fractionDigits:
                    raise ValueError("Wrong fraction digits for value %s allowed %s" % (strvalue, self.fractionDigits))
                        
        if self.maxExclusive is not None and value >= self.maxExclusive:
            raise ValueError("Value %s greater or equal to maxExclusive %s" %(value,self.maxExclusive))
        if self.maxInclusive is not None and value > self.maxInclusive:
            raise ValueError("Value %s greater than maxInclusive %s" %(value,self.maxInclusive))
        if self.minExclusive is not None and value <= self.minExclusive:
            raise ValueError("Value %s smaller or equal to minExclusive %s" %(value,self.minExclusive))
        if self.minInclusive is not None and value < self.minInclusive:
            raise ValueError("Value %s smaller than minInclusive %s" %(value,self.minInclusive))
        
        if self.pattern is not None:
            compiled_pattern = re.compile(self.pattern)
            if not compiled_pattern.match(str(value)):
                raise ValueError("Value %s doesn't match pattern %s." %(value, self.pattern))
            
        if self.totalDigits is not None:
            strvalue = str(value)
            l = len(strvalue)
            if strvalue.find(".") != -1:
                l = l - 1
            if l > self.totalDigits:
                raise ValueError("Number of total digits of %s is bigger than %s." % (strvalue, self.totalDigits))
            
        return value
     
    def accept(self, value):
        if value is None:
            return None
        elif isinstance(value, int) or isinstance(value, long) or isinstance(value, float):
            pass#value is just value
        elif isinstance(value, str):
            value = float(value)
        else:
            raise ValueError("Incorrect value '%s' for Decimal field." % value)
        
        self._check_restrictions(value)
        return value
        
          
    def xmlvalue(self, value):
        return str(value)
    
    def pythonvalue(self, xmlvalue):
        if xmlvalue == 'nil':
            return None
        else:
            return self.accept(xmlvalue)
        
        
        
class Integer(Decimal):
    def __init__(self, enumeration = None, maxExclusive=None, 
                 maxInclusive=None, minExclusive=None, minInclusive=None, 
                 pattern=None, totalDigits=None):
        super(Integer,self).__init__(enumeration = enumeration,fractionDigits=0, maxExclusive=maxExclusive, 
                 maxInclusive=maxInclusive, minExclusive=minExclusive, minInclusive=minInclusive, 
                 pattern=pattern, totalDigits=totalDigits)
        
    def accept(self, value):
        if value is None:
            return None
        elif isinstance(value, int) or isinstance(value, long):
            pass#value is just value continue.
        elif isinstance(value, str):
            value = int(value)
        else:
            raise ValueError("Incorrect value '%s' for Decimal field." % value)
        
        self._check_restrictions(value)
        return value
    
    
class Long(Integer):
    def __init__(self, enumeration = None, maxExclusive=None, 
                 maxInclusive=9223372036854775807, minExclusive=None, minInclusive=-9223372036854775808, 
                 pattern=None, totalDigits=None):
        super(Integer,self).__init__(enumeration = enumeration,fractionDigits=0, maxExclusive=maxExclusive, 
                                     maxInclusive=maxInclusive, minExclusive=minExclusive, minInclusive=minInclusive, 
                                     pattern=pattern, totalDigits=totalDigits)
                   
class Int(Long):
    def __init__(self, enumeration = None, maxExclusive=None, 
                 maxInclusive=2147483647, minExclusive=None, minInclusive=-2147483648, 
                 pattern=None, totalDigits=None):
        super(Integer,self).__init__(enumeration = enumeration,fractionDigits=0, maxExclusive=maxExclusive, 
                                     maxInclusive=maxInclusive, minExclusive=minExclusive, minInclusive=minInclusive, 
                                     pattern=pattern, totalDigits=totalDigits)
        
    
class Element(object):
    """Basic building block, represents a XML element that can appear one or zero
    times in XML that should be rendered as subelement e.g.
    <aircraft><tail_number>LN-KKY</tail_number></aircraft>
    Tail number is element. 
    For elements that can appear multiple times use ListElement."""
    _creation_counter = 0
    
    def __init__(self, _type, minOccurs = 1, tagname = None, nillable = False,
                 default = None):
        """:param _type: Class or instance of class that inherits from Type,
                         usually a child of SimpleType from xsd package,
                         or user defined class that inherits from ComplexType.
           :param minOccurs: int, how many times this object can appear in valid XML
                             can be 0 or 1. See: difference between Element and 
                             ListElement.
           :param tagname: str, name of tag when different to field declared in
                           ComplexType, important when tag name is python reserved 
                           work e.g. import
           :param nillable: bool, is object nilable.  
        """
        if not minOccurs in [0,1]: raise "minOccurs for Element can by only 0 or 1, use ListElement insted."
        self._creation_number = Element._creation_counter
        Element._creation_counter += 1
        self._passed_type = _type
        self._type = None#Will be evaluated when needed from _passed_type
        self._minOccurs = minOccurs
        self.tagname = tagname
        self.default = default
        self.nillable = nillable
        
    def _evaluate_type(self):
        if self._type is None:
            if isinstance(self._passed_type,str):
                self._passed_type = USER_TYPE_REGISTER.find_type(self._passed_type)
            if isinstance(self._passed_type, Type):
                self._type = self._passed_type
            else:
                self._type = self._passed_type()
        
    def empty_value(self):
        """Empty value methods is used when new object is constructed for 
        field initialization in most cases this should be None, but for lists 
        and other types of aggregates this should by an empty aggregate."""
        return self.default
    
    def accept(self,value):
        self._evaluate_type()
        """Checks is the value correct from type defined in constructions."""
        if value == NIL:
            if self.nillable:
                return NIL
            else:
                raise ValueError("Nil value for not nillable element.")  
        else:
            return self._type.accept(value)
    
    def render(self, parent, field_name, value, namespace=None,elementFormDefault=None):
        self._evaluate_type()
        if value is None:
            return
        #This allows complexType to redefine the name space a.k.a. 
        #to use name space different then parent's one.
        if hasattr(self._type,"NAMESPACE"):
            namespace = self._type.NAMESPACE
            
        if namespace:
            if hasattr(self._type,"ELEMENT_FORM_DEFAULT"):
                if self._type.ELEMENT_FORM_DEFAULT== ElementFormDefault.QUALIFIED:
                    field_name = "{%s}%s" % (namespace, field_name)
            else:
                if elementFormDefault == ElementFormDefault.QUALIFIED:
                    field_name = "{%s}%s" % (namespace, field_name)
            
        xmlelement = etree.Element(field_name)
        if value == NIL:
            xmlelement.set("{http://www.w3.org/2001/XMLSchema-instance}nil","true")
        else:
            self._type.render(xmlelement, value, namespace)
        parent.append(xmlelement)
        
    
    def parse(self, instance, field_name, xmlelement):
        self._evaluate_type()
        if xmlelement.get("{http://www.w3.org/2001/XMLSchema-instance}nil") == "true":
            value = NIL
        else:
            value = self._type.parse_xmlelement(xmlelement)
        setattr(instance, field_name, value)
    
    def __repr__(self):
        if isinstance(self._type,str):
            return "%s<%s>" %  (self.__class__.__name__,self._type)
        else:
            return "%s<%s>" %  (self.__class__.__name__,self._type.__class__.__name__)
    
    
    
class ClassNamedElement(Element):
    """Use this element when tagname should be based on class name in rendering time."""
    def __init__(self,_type, minOccurs = 1, nilable = False):
        super(ClassNamedElement, self).__init__(_type, minOccurs,None,nilable)
        
    def render(self, parent, field_name, value, namespace=None,elementFormDefault=None):
        if value is None:
            return
        if hasattr(value,"NAMESPACE"):
            namespace = value.NAMESPACE
            
        if namespace and elementFormDefault==ElementFormDefault.QUALIFIED:
            tagname = "{%s}%s" % (namespace, uncapitalize(value.__class__.__name__))
        else:
            tagname = value.__class__.__name__
        xmlelement = etree.Element(tagname)
        self._type.render(xmlelement, value)
        parent.append(xmlelement)
    
    
    
class Attribute(Element): 
    """Represents a field that is a XML attribute. e.g.
    <person name="Jhon" surname="Dough">
        <job>Programmer<job>
    </person>
    name and surname are attributes. Attribute type can be only simple types."""
    def __init__(self,type_clazz, use=Use.REQUIRED, tagname = None,nillable = False,
                 default=None):
        """
        :param type_clazz: Only simple tapes are accepted: String, Integer etc.
        """
        if use == Use.REQUIRED:
            minOccurs = 1
        else:
            minOccurs = 0
        super(Attribute, self).__init__(type_clazz, tagname=tagname, minOccurs = minOccurs)
        self.nillable = nillable
        self.use = use
        self.default = default
        
    def render(self, parent, field_name, value, namespace=None,elementFormDefault=None):
        self._evaluate_type()
        if value is None:
            if self._minOccurs:
                raise ValueError("Value None is not acceptable for required field.")
            else:
                return
        elif value == NIL:
            if self.nillable:
                xmlvalue = "nil"
            else:
                raise ValueError("Nil value for not nillable Attribute.")
        else: 
            xmlvalue = self._type.xmlvalue(value)
        parent.set(field_name, xmlvalue)
        
    def parse(self, instance, field_name, xmlelement):
        self._evaluate_type()
        xmlvalue = xmlelement.get(field_name)
        if xmlvalue is None:
            xmlvalue = self.default
        value = self._type.pythonvalue(xmlvalue)
        setattr(instance, field_name, value)
        
        
class Ref(Element):
    """References are not fields, they point to type that has them - usually groups.
    With Ref fields will be rendered directly into parent object. e.g.
    class Person(xsd.Group):
        name = xsd.Element(xsd.String)
        surname = xsd.Element(xsd.String)
    class Job(xsd.ComplexType):
        title = xsd.Element(xsd.String)
        person = xsd.Ref(Person)
    The valid XML will be:
    <job>
        <title>Programmer</title>
        <name>An</name>
        <surname>Brown</surname>
    </job>
    Note that name and surname are not wrapped with <person> tag.
    """
    def empty_value(self):
        return copy(self._type)
    
    def render(self, parent, field_name, value, namespace=None):
        if value is None:
            if self._required:
                raise ValueError("Value None is not acceptable for required field.")
            else:
                return
        self._type.render(parent, value, namespace)
        
class Content(Ref):
    """Direct access to element.text. Note that <> will be escaped."""
    def empty_value(self):
        return None
        
        
class ListElement(Element):
    """Tag element that can appear many times in valid XML. e.g.
    <flight>
        <aircraft>G-ABCD</aircraft>
        <passenger>John Backus</passenger>
        <passenger>Kent Beck</passenger>
        <passenger>Larry Breed</passenger>
    </flight>
    passenger is an example of ListElement, the definition would look:
    passengers = xsd.ListElement(xsd.String, "passenger")
    Note that tag name is required for this field, as the field name should 
    be in plural form, and tag usually is not.
    """
    def __init__(self, clazz, tagname, minOccurs=None,maxOccurs=None,nillable=False):
        super(ListElement,self).__init__(clazz,tagname=tagname,nillable=nillable)
        self._maxOccurs = maxOccurs
        self._minOccurs = minOccurs

    def accept(self,value):
        return value
    
    def empty_value(this):
        class TypedList(list):
            def append(self,value):
                this._evaluate_type()
                if value == NIL:
                    if this.nillable:
                        accepted_value = NIL
                    else:
                        raise ValueError("Nil value in not nillable list.")
                else:
                    accepted_value = this._type.accept(value)
                if this._maxOccurs is not None and this._maxOccurs != UNBOUNDED:
                    if (len(self)+1)>this._maxOccurs:
                        raise ValueError("Number of items in list %s is would be bigger than maxOccurs %s" %( len(self), this._maxOccurs))
                super(TypedList,self).append(accepted_value)
        return TypedList()         
    
   
    def render(self, parent, field_name, value, namespace=None,elementFormDefault=None):
        self._evaluate_type()
        items = value#The value must be list of items.
        if self._minOccurs and len(items) < self._minOccurs:
            raise ValueError("For %s minOccurs=%d but list length %d." %(field_name, self._minOccurs, len(items)))
        if self._maxOccurs and len(items) > self._maxOccurs:
            raise ValueError("For %s maxOccurs=%d but list length %d." % (field_name, self._maxOccurs))
        
        for item in items:
            if namespace:
                tagname = "{%s}%s" % (namespace,self.tagname)
            else:
                tagname = self.tagname
            xmlelement = etree.Element(tagname)
            if item == NIL:
                xmlelement.set("{http://www.w3.org/2001/XMLSchema-instance}nil","true")
            else:
                self._type.render(xmlelement, item, namespace)
            parent.append(xmlelement)
            
            
    def parse(self, instance, field_name, xmlelement):
        self._evaluate_type()
        if xmlelement.get("{http://www.w3.org/2001/XMLSchema-instance}nil"):
            value = NIL
        else:
            value = self._type.parse_xmlelement(xmlelement)
        _list = getattr(instance, field_name)
        _list.append(value)
        
        
                
class ComplexTypeMetaInfo(object): 
    def __init__(self,cls):
        self.cls = cls
        self.fields = []
        self.attributes = []
        self.groups = []
        for attr in dir(cls):
            item = getattr(cls,attr)
            if isinstance(getattr(cls,attr),Attribute):
                item._name = attr
                self.attributes.append(item)
            elif isinstance(item, Ref):
                item._name = attr
                self.groups.append(item)
            elif isinstance(item, Element):
                item._name = attr
                self.fields.append(item)
        self.fields = sorted(self.fields, key=lambda f: f._creation_number)
        self.attributes = sorted(self.attributes, key=lambda f: f._creation_number)
        self.groups = sorted(self.groups, key=lambda f: f._creation_number)
        self.allelements = sorted(self.fields+self.groups, key=lambda f: f._creation_number)
        self.all = sorted(self.fields+self.groups+self.attributes, key=lambda f: f._creation_number)
        
        
        
class Complex_PythonType(Type_PythonType):
    """Python type for ComplexType, builds _meta object for every class that 
    inherit from ComplexType. """
    def __new__(cls,name,bases,attrs):
        newcls = super(Complex_PythonType,cls).__new__(cls,name,bases,attrs)
        if name != 'Complex':
            newcls._meta = ComplexTypeMetaInfo(newcls)
        return newcls
    
    
    
class ComplexType(Type):
    """Parent for XML elements that have sub-elements."""
    INDICATOR = Sequence#Indicator see: class Indicators. To be defined in sub-type.
    INHERITANCE = None#Type of inheritance see: class Inheritance, to be defined in sub-type.
    NAMESPACE = None#String, preferably URL with name space for this element. Is set be Scheme instance.
    ELEMENT_FORM_DEFAULT = None#String, one of two values.
    
    __metaclass__ = Complex_PythonType
    
    def __new__(cls,*args,**kwargs):
        instance = super(ComplexType,cls).__new__(cls)
        for field in instance._meta.all:
            setattr(instance,field._name,field.empty_value())
        return instance

    def __init__(self,**kwargs):
        for key,value in kwargs.items():
            setattr(self,key,value)
                
    def __setattr__(self, attr, value):
        if attr == "_xmlelement":
            super(ComplexType,self).__setattr__(attr,value)
        else:
            try:
                field = self._find_field(self._meta.all, attr)
            except IndexError:
                raise AttributeError("Model '%s' doesn't have attribute '%s'." % (self.__class__.__name__,attr))
            super(ComplexType,self).__setattr__(attr,field.accept(value))
        
        
    def accept(self, value):
        """Instance methods that validate other instance."""
        if value is None:
            return None
        elif isinstance(value,self.__class__):
            return value
        else:
            raise ValueError('Wrong value object type %s for %s.' % (value,self.__class__.__name__))
        
            
    def render(self, parent, instance, namespace=None):
        if instance is None: return None
        for field in instance._meta.all: 
            if self.ELEMENT_FORM_DEFAULT == ElementFormDefault.QUALIFIED:
                field.render(
                    parent = parent, 
                    field_name = field._name, 
                    value = getattr(instance, field._name), 
                    namespace = self.NAMESPACE,
                    elementFormDefault=self.ELEMENT_FORM_DEFAULT)
            else:
                field.render(
                    parent = parent, 
                    field_name = field._name, 
                    value = getattr(instance, field._name))
    
    @classmethod
    def _find_field(cls, fields, name):
        return filter(lambda f:f._name == name,fields)[0]
    
    @classmethod
    def _get_field_by_name(cls, fields, field_name):
        for field in fields:
            if field.tagname == field_name or field._name == field_name:
                return field
        raise ValueError("Field not found '%s', fields: %s" %(field_name, fields))

       
    @classmethod  
    def _find_subelement(cls, field, xmlelement):
        def gettagns(tag):
            """Translates tag string in format {namespace}
            tag to tuple (namespace,tag)."""
            if tag[:1] == "{":
                return tag[1:].split("}", 1)
            else:
                return (None,tag)
        #--------------------------------------------
        subelements = []
        for subelement in xmlelement:
            if isinstance(subelement, etree._Comment):
                continue
            ns, tag = gettagns(subelement.tag)
            if tag == field._name or tag == field.tagname:
                subelements.append(subelement)
        return subelements
         
         
    @classmethod
    def parse_xmlelement(cls, xmlelement):    
        instance = cls()
        instance._xmlelement = xmlelement
        for attribute in instance._meta.attributes:
            attribute.parse(instance, attribute._name, xmlelement)
                
        for field in instance._meta.fields:
            subelements = cls._find_subelement(field, xmlelement)
            for subelement in subelements:
                field.parse(instance, field._name, subelement)
                
        for group in instance._meta.groups:
            group.parse(instance, group._name, xmlelement)
                
        return instance
    
    
    @classmethod
    def __parse_with_validation(cls, xml, schema):
        from py2xsd import generate_xsd
        schema = generate_xsd(schema)
        schemaelement = etree.XMLSchema(schema)
        parser = etree.XMLParser(schema = schemaelement)
        xmlelement = etree.fromstring(xml, parser)
        return xmlelement
    
    
    @classmethod
    def parsexml(cls, xml, schema=None):
        if schema:
            xmlelement = cls.__parse_with_validation(xml, schema)
        else:
            xmlelement = etree.fromstring(xml)
        return cls.parse_xmlelement(xmlelement)
        
        
    def xml(self, tagname, schema=None):
        if self.NAMESPACE:
            tagname = "{%s}%s" % (self.NAMESPACE, tagname)
        xmlelement = etree.Element(tagname)
        self.render(xmlelement, self, self.NAMESPACE)
        xml = etree.tostring(xmlelement, pretty_print=True)
        if schema:
            self.__parse_with_validation(xml, schema)
        return xml
    
    
    @classmethod
    def _force_elements_type_evalution(cls):
        """Allows schema object to force elements type evalution for XSD generation"""
        for element in cls._meta.all:
            element._evaluate_type()
     

  
class Group(ComplexType):
    """Parent object for XSD Groups. Marker. Must be use with Ref."""
    pass

class AttributeGroup(Group):
    """Parent object for XSD Attribute Groups. Marker. Must be use with Ref."""
    pass

class Document(ComplexType):
    """Represents whole xml, is expected to have only one field the root."""
    class MockElement(object):
        def __init__(self):
            self.element = None
        def append(self, element):
            self.element = element
            
    def render(self):
        field = self._meta.fields[0]#The only field
        mockelement = Document.MockElement()
        instance = getattr(self, field._name)
        field.render(mockelement, field._name, instance, self.NAMESPACE)
        return etree.tostring(mockelement.element, pretty_print=True)
    
    #TODO:schema support
    @classmethod
    def parsexml(cls, xml):
        field = cls._meta.fields[0]#The only field
        xmlelement = etree.fromstring(xml)
        field.parse(cls, field._name, xmlelement)
        
        
    


class List(SimpleType):
    pass

class AnyURI(String):
    pass

class QName(String):
    pass

class NMTOKEN(String):
    pass

class NMTOKENS(String):
    pass

    
class Schema(object):
    """Main object for XSD schema. This object is required for XSD and WSDLgeneration
        and correct namespaces as it propagates targetNamespace to all objects.
        Instance of this is expected to be named Schema. """
    def __init__(self,targetNamespace, elementFormDefault=ElementFormDefault.UNQUALIFIED ,simpleTypes=[], attributeGroups=[], groups=[], complexTypes=[], elements={}):
        """
        :param targetNamespace: string, xsd namespace URL.
        :param elementFormDefault: unqualified/qualified Defines should namespace 
        be used in child elements. Suggested: qualified. Default: unqualified as 
        it is default in XSD.
        :param simpleTypes: List of objects that extend xsd.SimpleType.
        :param attributeGroups: List of objects that extend xsd.AttributeGroup.
        :param groups: List of objects that extend xsd.Group.
        :param complexTypes: List of complexTypes class. 
        :param elements: dict of xsd.Elements that are direct schema elements.
        """
        self.targetNamespace = targetNamespace
        self.elementFormDefault = elementFormDefault
        self.simpleTypes = simpleTypes
        self.attributeGroups = attributeGroups
        self.groups = groups
        self.complexTypes = complexTypes
        self.elements = elements
        
        self.__init_namespace(self.simpleTypes)
        self.__init_namespace(self.groups)
        self.__init_namespace(self.attributeGroups)
        self.__init_namespace(self.complexTypes)
        
        self._force_elements_type_evalution(self.complexTypes)
        self._force_elements_type_evalution(self.attributeGroups)
        self._force_elements_type_evalution(self.groups)
        
        for element in self.elements.values():
            element._evaluate_type()
        
        
        
    def __init_namespace(self, types):
        for _type in types:
            _type.NAMESPACE = self.targetNamespace
            _type.ELEMENT_FORM_DEFAULT = self.elementFormDefault
            
    
    def _force_elements_type_evalution(self, types):
        for t in types:
            t._force_elements_type_evalution()
            
            
class Method(object):
    """Method description. The main information is mapping soapAction and operationName
    to function for dispatcher. input and output mapping informs how and which
    objects should be created on incoming/outgoing messages."""
    def __init__(self, operationName, soapAction, input, output, function=None):
        """:param function: The function that should be called. Required only for server."""
        self.operationName = operationName
        self.soapAction = soapAction
        self.input = input
        self.output = output
        self.function = function
        

    



        
    