"""
Design Decision Log.

1. I have decided to not use dews/dexml approach to field description as it doesn't give good distinction between
   element and attribute. It is not a problem when parsing a XML, but it is quite important for rendering and XSD
   generation. The new syntax will look like:

    tail_number = xsd.Attribute(xsd.String)
    flight_number = xsd.Element(xsd.Integer)

   which makes this distinction clear.

2. Render will take value/instance as parameter. More obvious would be if render just rendered current object, but
   this approach doesn't work with Python simple types like string. Where you can not call 'x'.render() so type method
   render must take a value as a parameter, which may same odd for complex types.

3. Due to render taking a value as parameter it could be implemented as a static/class method, but it is not.
   xsd.Element takes a class or an instance, but if class was passed it will create an instance - so a parameter-less
   constructor is required. Reason for that is to keep API consistent. There are two syntaxes:

   a. xsd.Element(xsd.String)
   b. xsd.Element(xsd.String(enumeration=['A', 'B']))

   because instance is required in case (b). creating it from class in case (a) makes other methods independent from
   this two syntaxes.

For information on XML schema validation, see https://lxml.de/validation.html#xmlschema
"""

import copy
import decimal
import enum
import functools
import importlib
import itertools
import logging
import re
from datetime import datetime, time, timedelta, timezone

import iso8601
from lxml import etree

from . import namespaces as ns
from .utils import timezone_offset_to_string
from .xsd_types import XSDDate

logger = logging.getLogger(__name__)

NIL = object()
UNBOUNDED = decimal.Decimal('infinity')


class CallStyle(str, enum.Enum):
    DOCUMENT = 'document'
    RPC = 'rpc'


class Use(str, enum.Enum):
    OPTIONAL = 'optional'
    REQUIRED = 'required'
    PROHIBITED = 'prohibited'


class Inheritance(str, enum.Enum):
    RESTRICTION = 'RESTRICTION'
    EXTENSION = 'EXTENSION'


class ElementFormDefault(str, enum.Enum):
    QUALIFIED = 'qualified'
    UNQUALIFIED = 'unqualified'


class Indicator:
    __slots__ = ['fields']

    def __init__(self, fields):
        self.fields = fields


class Sequence(Indicator):
    pass


class Choice(Indicator):
    pass


class All(Indicator):
    pass


class Type:
    def accept(self, value):
        raise NotImplementedError

    def parse_xmlelement(self, xmlelement):
        raise NotImplementedError

    def parsexml(self, xml):
        raise NotImplementedError

    def render(self, parent, value):
        raise NotImplementedError


class SimpleType(Type):
    def render(self, parent, value, namespace, elementFormDefault):
        parent.text = self.xmlvalue(value)

    def parse_xmlelement(self, xmlelement):
        return self.pythonvalue(xmlelement.text)

    def xmlvalue(self, value):
        raise NotImplementedError

    def pythonvalue(self, xmlvalue):
        raise NotImplementedError


class String(SimpleType):
    # To be defined in children.
    enumeration = None
    pattern = None
    length = None
    minLength = None
    maxLength = None
    whiteSpace = None

    def __init__(self, enumeration=None, pattern=None, length=None, minLength=None, maxLength=None, whiteSpace=None):
        # Override static values
        if enumeration is not None:
            self.enumeration = enumeration
        if pattern is not None:
            self.pattern = pattern
        if length is not None:
            self.length = length
        if minLength is not None:
            self.minLength = minLength
        if maxLength is not None:
            self.maxLength = maxLength
        if whiteSpace is not None:
            self.whiteSpace = whiteSpace

    def accept(self, value):
        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError("Value %r for class '%s'." % (value, self.__class__.__name__))

        value = self._clean_whitespace(value)

        if self.pattern:
            pattern = self.pattern + '$'
            if re.match(pattern, value) is None:
                raise ValueError("Value '%s' doesn't match pattern '%s'" % (value, self.pattern))

        if self.enumeration:
            if not (value in self.enumeration):
                raise ValueError("Value '%s' not in list %s." % (value, self.enumeration))

        if self.length:
            if len(value) != self.length:
                raise ValueError("Value '%s' length %s expected." % (value, self.length))

        if self.minLength:
            if len(value) < self.minLength:
                raise ValueError("Value '%s' minLength %s expected." % (value, self.minLength))

        if self.maxLength:
            if len(value) > self.maxLength:
                raise ValueError("Value '%s' maxLength %s expected." % (value, self.maxLength))

        return value

    def xmlvalue(self, value):
        return value

    def pythonvalue(self, xmlvalue):
        return xmlvalue

    def _clean_whitespace(self, value):
        if self.whiteSpace == 'preserve':
            # do nothing, just preserve the value
            pass
        elif self.whiteSpace == 'replace':
            # replace line feeds, tabs, spaces, and carriage returns with whitespaces
            value = re.sub(r'[\t\r\n\s]', ' ', value)
        elif self.whiteSpace == 'collapse':
            # clean line feeds, tabs, spaces, and carriage returns with one whitespace
            value = re.sub(r'[\t\r\n\s]+', ' ', value)

        return value


class Boolean(SimpleType):
    def accept(self, value):
        if value in [True, False, None]:
            return value
        else:
            raise ValueError("Value '%s' for class '%s'." % (str(value), self.__class__.__name__))

    def xmlvalue(self, value):
        if value is False:
            return 'false'
        elif value is True:
            return 'true'
        elif value is None:
            return 'nil'
        else:
            raise ValueError("Value '%s' for class '%s'." % (str(value), self.__class__.__name__))

    def pythonvalue(self, value):
        if value == 'false':
            return False
        elif value == 'true':
            return True
        elif value == 'nil' or value is None:
            return None
        else:
            raise ValueError('Boolean value error - %s' % value)


class Date(SimpleType):
    # Example text value: 2001-10-26+02:00
    # Does currently not support any constraining facets:
    #   https://www.w3.org/TR/2001/REC-xmlschema-2-20010502/#date
    #   3.2.9.2 Constraining facets

    YEAR_MONTH_DAY_REGEX = re.compile(r'''
        ^(\-)?
        (?P<year>\d{4,})\-(?P<month>\d{2})\-(?P<day>\d{2})
        (?P<timezone>Z|((?P<tz_sign>[-+])(?P<tz_hour>[0-9]{2}):?(?P<tz_minute>[0-9]{2})?))?$''', re.VERBOSE)

    def accept(self, value):
        if value is None:
            return None
        elif isinstance(value, XSDDate):
            return value
        time_components = ('hour', 'minute', 'second', 'microsecond')
        has_time_compontent = any(hasattr(value, key) for key in time_components)
        if (hasattr(value, 'year') and hasattr(value, 'month') and hasattr(value, 'day')) and not has_time_compontent:
            tz = getattr(value, 'tzinfo', None)  # support datetime.date
            return XSDDate(value.year, value.month, value.day, tzinfo=tz)
        raise ValueError('Incorrect type value %r for date field.' % value)

    def xmlvalue(self, value):
        timestring_without_tz = value.strftime('%Y-%m-%d')
        tz = getattr(value, 'tzinfo', None)
        if not tz:
            return timestring_without_tz
        return timestring_without_tz + timezone_offset_to_string(tz.utcoffset(None))

    def pythonvalue(self, value):
        if value is None or value == 'nil':
            return None
        if not isinstance(value, str):
            raise ValueError('Expected a string, not %r' % value)

        match = self.YEAR_MONTH_DAY_REGEX.match(value)
        if match is None:
            raise ValueError('Unable to parse date string %r' % value)
        year = int(match.group('year'))
        month = int(match.group('month'))
        day = int(match.group('day'))
        tz = self._parse_tz(match)
        return XSDDate(year, month, day, tzinfo=tz)

    def _parse_tz(self, match):
        offset = match.group('timezone')
        if not offset:
            return None
        elif offset == 'Z':
            return timezone.utc

        sign = 1 if match.group('tz_sign') == '+' else -1
        hours = int(match.group('tz_hour'))
        minutes = int(match.group('tz_minute'))
        return timezone(sign * timedelta(hours=hours, minutes=minutes), name='UTC' + offset)


class DateTime(SimpleType):
    # Example text value: 2001-10-26T21:32:52

    def accept(self, value):
        if value is None:
            return None
        elif isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            return iso8601.parse_date(value)
        raise ValueError("Incorrect type value '%s' for DateTime field." % value)

    def xmlvalue(self, value):
        if value is None:
            return 'nil'
        timestring_without_tz = value.strftime('%Y-%m-%dT%H:%M:%S')
        tz = value.tzinfo
        if not tz:
            return timestring_without_tz
        return timestring_without_tz + timezone_offset_to_string(tz.utcoffset(value))

    def pythonvalue(self, value):
        return None if value is None or value == 'nil' else iso8601.parse_date(value)


class Time(SimpleType):
    # Example text value: 21:32:52

    def accept(self, value):
        if value is None:
            return None
        elif isinstance(value, time):
            return value
        elif isinstance(value, str):
            return self._parse(value)
        raise ValueError("Incorrect type value '%s' for Time field." % value)

    def xmlvalue(self, value):
        if value is None:
            return 'nil'
        timestring_without_tz = value.strftime('%H:%M:%S')
        tz = value.tzinfo
        if not tz:
            return timestring_without_tz
        return timestring_without_tz + timezone_offset_to_string(tz.utcoffset(None))

    def pythonvalue(self, value):
        return None if value is None or value == 'nil' else self._parse(value)

    @staticmethod
    def _parse(value):
        # Horrible hacky approach to implement this quickly:
        try:
            dt = iso8601.parse_date('1900-01-01T' + value)
        except Exception as e:
            raise ValueError(str(e)) from e
        else:
            return dt.time().replace(tzinfo=dt.tzinfo)


class Decimal(SimpleType):

    def __init__(self, enumeration=None, fractionDigits=None, maxExclusive=None,
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
            raise ValueError('%s not in enumeration %s' % (value, self.enumeration))

        if self.fractionDigits is not None:
            strvalue = str(value)
            if self.fractionDigits == 0:
                if '.' in strvalue:
                    raise ValueError('Wrong fraction digits for value %s allowed %s' % (strvalue, self.fractionDigits))
            else:
                if '.' not in strvalue:
                    raise ValueError('Wrong fraction digits for value %s allowed %s' % (strvalue, self.fractionDigits))
                fr = strvalue.split('.')[1]
                if len(fr) != self.fractionDigits:
                    raise ValueError('Wrong fraction digits for value %s allowed %s' % (strvalue, self.fractionDigits))

        if self.maxExclusive is not None and value >= self.maxExclusive:
            raise ValueError('Value %s greater or equal to maxExclusive %s' % (value, self.maxExclusive))
        if self.maxInclusive is not None and value > self.maxInclusive:
            raise ValueError('Value %s greater than maxInclusive %s' % (value, self.maxInclusive))
        if self.minExclusive is not None and value <= self.minExclusive:
            raise ValueError('Value %s smaller or equal to minExclusive %s' % (value, self.minExclusive))
        if self.minInclusive is not None and value < self.minInclusive:
            raise ValueError('Value %s smaller than minInclusive %s' % (value, self.minInclusive))

        if self.pattern is not None:
            pattern = self.pattern + '$'
            if re.match(pattern, str(value)) is None:
                raise ValueError("Value %s doesn't match pattern %s." % (value, self.pattern))

        if self.totalDigits is not None:
            strvalue = str(value)
            length = len(strvalue)
            if '.' in strvalue:
                length -= 1
            if length > self.totalDigits:
                raise ValueError('Number of total digits of %s is bigger than %s.' % (strvalue, self.totalDigits))

        return value

    def accept(self, value):
        if value is None:
            return None
        elif isinstance(value, decimal.Decimal):
            value = str(value)
        elif isinstance(value, (float, int)):
            pass  # value is just value
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


class Double(Decimal):
    def __init__(self, enumeration=None, maxExclusive=None, maxInclusive=None, minExclusive=None, minInclusive=None,
                 pattern=None):
        super().__init__(
            enumeration=enumeration, maxExclusive=maxExclusive, maxInclusive=maxInclusive, minExclusive=minExclusive,
            minInclusive=minInclusive, pattern=pattern,
        )


class Float(Decimal):
    def __init__(self, enumeration=None, maxExclusive=None, maxInclusive=None, minExclusive=None, minInclusive=None,
                 pattern=None):
        super().__init__(
            enumeration=enumeration, maxExclusive=maxExclusive, maxInclusive=maxInclusive, minExclusive=minExclusive,
            minInclusive=minInclusive, pattern=pattern,
        )


class Integer(Decimal):
    overrides = {'fractionDigits': 0, 'pattern': r'[-+]?[0-9]+'}

    def __init__(self, enumeration=None, fractionDigits=None, maxExclusive=None, maxInclusive=None, minExclusive=None,
                 minInclusive=None, pattern=None, totalDigits=None):
        facets = {k: v for k, v in locals().items() if k not in {'self', '__class__'}}
        for c in itertools.dropwhile(lambda x: x != Integer, reversed(self.__class__.__mro__)):
            facets.update(c.overrides)
        super().__init__(**facets)

    def accept(self, value):
        if value is None:
            return None
        elif isinstance(value, int):
            pass  # value is just value continue.
        elif isinstance(value, str):
            value = int(value)
        else:
            raise ValueError("Incorrect value '%s' for Decimal field." % value)

        self._check_restrictions(value)
        return value


class NonNegativeInteger(Integer):
    overrides = {'minInclusive': 0}


class NonPositiveInteger(Integer):
    overrides = {'maxInclusive': 0}


class NegativeInteger(NonPositiveInteger):
    overrides = {'maxInclusive': -1}


class PositiveInteger(NonNegativeInteger):
    overrides = {'minInclusive': 1}


class Long(Integer):
    overrides = {'maxInclusive': 9223372036854775807, 'minInclusive': -9223372036854775808}


class Int(Long):
    overrides = {'maxInclusive': 2147483647, 'minInclusive': -2147483648}


class Short(Int):
    overrides = {'maxInclusive': 32767, 'minInclusive': -32768}


class Byte(Short):
    overrides = {'maxInclusive': 127, 'minInclusive': -128}


class UnsignedLong(NonNegativeInteger):
    overrides = {'minInclusive': 0, 'maxInclusive': 18446744073709551615}


class UnsignedInt(UnsignedLong):
    overrides = {'minInclusive': 0, 'maxInclusive': 4294967295}


class UnsignedShort(UnsignedInt):
    overrides = {'minInclusive': 0, 'maxInclusive': 65535}


class UnsignedByte(UnsignedShort):
    overrides = {'minInclusive': 0, 'maxInclusive': 255}


class MaxOccurs(SimpleType):
    def accept(self, value):
        if value is None:
            return None
        elif value in ('unbounded', UNBOUNDED):
            return UNBOUNDED
        else:
            return int(value)

    def xmlvalue(self, value):
        return 'unbounded' if value == UNBOUNDED else str(value)

    def pythonvalue(self, xmlvalue):
        return self.accept(xmlvalue)


def import_type(type_name):
    if '.' not in type_name:
        raise ValueError('We need the full namepath to be able to import it: %s' % type_name)
    module, name = type_name.rsplit('.', 1)
    module = importlib.import_module(module)
    return getattr(module, name)


class Element:
    """
    Basic building block, represents an XML element that can appear 0 or 1 times that should be rendered as subelement.

    e.g. <aircraft><tail_number>LN-KKY</tail_number></aircraft> Tail number is element. For elements that can appear
    multiple times use ListElement.
    """

    _creation_counter = 0

    def __init__(self, _type, minOccurs=1, tagname=None, nillable=False, default=None, namespace=None, substitutionGroup=None):
        """
        :param _type: Class or instance of class that inherits from Type,
                      usually a child of SimpleType from the xsd package, or
                      a user defined class that inherits from ComplexType.
        :param minOccurs: int, how many times this object can appear in valid
                          XML can be 0 or 1. See: difference between Element
                          and ListElement.
        :param tagname: str, name of tag when different to field declared in
                        ComplexType, important when the tag name is a Python
                        keyword e.g. "import"
        :param nillable: bool, is object nilable.
        """
        if minOccurs not in (0, 1):
            raise ValueError('minOccurs for Element can be only 0 or 1, use ListElement instead.')
        self._creation_number = Element._creation_counter
        Element._creation_counter += 1
        self._passed_type = _type
        self._type = None  # Will be evaluated when needed from _passed_type
        self._minOccurs = minOccurs
        self.tagname = tagname
        self.default = default
        self.nillable = nillable
        self.namespace = namespace
        self.substitutionGroup = substitutionGroup

    def _evaluate_type(self):
        if self._type is None:
            if isinstance(self._passed_type, str):
                self._passed_type = import_type(self._passed_type)
            if isinstance(self._passed_type, Type):
                self._type = self._passed_type
            else:
                self._type = self._passed_type()

    def empty_value(self):
        """
        Empty value used when a new object is constructed for a field.

        initialization in most cases this should be None, but for lists and other types of aggregates this should be
        an empty aggregate.
        """
        return self.default

    def xsd_elements(self):
        return (self, )

    def accept(self, value):
        """Check if the value correct from type defined in constructions."""
        self._evaluate_type()
        if value is NIL:
            if self.nillable:
                return NIL
            else:
                raise ValueError('Nil value for not nillable element.')
        else:
            return self._type.accept(value)

    def render(self, parent, field_name, value, namespace=None, elementFormDefault=None):
        self._evaluate_type()
        if value is None:
            return

        if self.namespace is not None:
            namespace = self.namespace
        if namespace is not None and elementFormDefault == ElementFormDefault.QUALIFIED:
            field_name = f'{{{namespace}}}{field_name}'

        xmlelement = etree.Element(field_name)
        if value is NIL:
            xmlelement.set(f'{{{ns.xsi}}}nil', 'true')
        else:
            self._type.render(xmlelement, value, namespace, elementFormDefault)
        parent.append(xmlelement)

    def parse(self, instance, field_name, xmlelement):
        self._evaluate_type()
        value = NIL if xmlelement.get(f'{{{ns.xsi}}}nil') == 'true' else self._type.parse_xmlelement(xmlelement)
        setattr(instance, field_name, value)

    def __repr__(self):
        x = self._type if isinstance(self._type, str) else self._type.__class__.__name__
        return f'{self.__class__.__name__}<{x}>'


class ClassNamedElement(Element):
    """Use this element when tagname should be based on class name in rendering time."""

    def __init__(self, _type, minOccurs=1, nilable=False):
        super().__init__(_type, minOccurs, None, nilable)

    def render(self, parent, field_name, value, namespace=None, elementFormDefault=None):
        if value is None:
            return
        tagname = value.name
        value = value.value
        if value is None:
            return

        namespace = value.SCHEMA.targetNamespace
        if namespace:
            tagname = f'{{{namespace}}}{tagname}'

        xmlelement = etree.Element(tagname)
        self._type.render(xmlelement, value, namespace=namespace, elementFormDefault=value.SCHEMA.elementFormDefault)
        parent.append(xmlelement)


class Attribute(Element):
    """
    Represents a field that is a XML attribute.

    e.g. <person name="Jhon" surname="Dough"><job>Programmer<job></person>
    name and surname are attributes. Attribute type can be only simple types.
    """

    def __init__(self, type_clazz, use=Use.REQUIRED, tagname=None, nillable=False, default=None):
        """:param type_clazz: Only simple tapes are accepted: String, Integer etc."""
        minOccurs = 1 if use == Use.REQUIRED else 0
        super().__init__(type_clazz, tagname=tagname, minOccurs=minOccurs)
        self.nillable = nillable
        self.use = use
        self.default = default

    def render(self, parent, field_name, value, namespace=None, elementFormDefault=None):
        self._evaluate_type()
        if value is None:
            if self._minOccurs:
                raise ValueError('Value None is not acceptable for required field.')
            else:
                return
        elif value is NIL:
            if self.nillable:
                xmlvalue = 'nil'
            else:
                raise ValueError('Nil value for not nillable Attribute.')
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
    """
    References are not fields, they point to a type that has them - usually groups.
    Ref fields will be rendered directly into the parent object. e.g.

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

    Note that name and surname are not wrapped with a <person> tag (because
    Person is a xsd.Group).
    """

    def empty_value(self):
        self._evaluate_type()
        return copy.copy(self._type)

    def render(self, parent, field_name, value, namespace=None, elementFormDefault=None):
        if value is None:
            if self._required:
                raise ValueError('Value None is not acceptable for required field.')
            else:
                return

        if isinstance(value, Group):
            self._type.render(parent, value, namespace, elementFormDefault)
            return

        tagname = f'{{{namespace}}}{field_name}' if namespace else field_name
        ref_element = etree.Element(tagname)
        self._type.render(ref_element, value, namespace, elementFormDefault)
        parent.append(ref_element)


class Content(Ref):
    """Direct access to element.text. Note that <> will be escaped."""

    def empty_value(self):
        return None


class TypedList(list):
    def __init__(self, element):
        super().__init__()
        self._list = element

    def append(self, value):
        self._list._evaluate_type()
        if value is NIL:
            if not self._list.nillable:
                raise ValueError('Nil value in not nillable list.')
            accepted_value = NIL
        else:
            accepted_value = self._list._type.accept(value)
        if self._list._maxOccurs is not None and (len(self) + 1 > self._list._maxOccurs):
            raise ValueError('You must not add more than %s items to this list.' % self._list._maxOccurs)
        super().append(accepted_value)


class ListElement(Element):
    """
    Tag element that can appear many times in valid XML. e.g.

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

    def __init__(self, clazz, tagname, minOccurs=None, maxOccurs=None, nillable=False, namespace=None):
        super().__init__(clazz, tagname=tagname, nillable=nillable, namespace=namespace)
        self._maxOccurs = maxOccurs
        self._minOccurs = minOccurs

    def accept(self, value):
        return value

    def empty_value(self):
        return TypedList(self)

    def render(self, parent, field_name, value, namespace=None, elementFormDefault=None):
        self._evaluate_type()
        items = value  # The value must be list of items.
        if self._minOccurs and len(items) < self._minOccurs:
            raise ValueError('For %s minOccurs=%d but list length %d.' % (field_name, self._minOccurs, len(items)))
        if self._maxOccurs and len(items) > self._maxOccurs:
            raise ValueError('For %s maxOccurs=%d but list length %d.' % (field_name, self._maxOccurs, len(items)))

        if self.namespace is not None:
            namespace = self.namespace
        if namespace is not None and elementFormDefault == ElementFormDefault.QUALIFIED:
            tagname = f'{{{namespace}}}{self.tagname}'
        else:
            tagname = self.tagname

        for item in items:
            xmlelement = etree.Element(tagname)
            if item is NIL:
                xmlelement.set(f'{{{ns.xsi}}}nil', 'true')
            else:
                self._type.render(xmlelement, item, namespace, elementFormDefault)
            parent.append(xmlelement)

    def parse(self, instance, field_name, xmlelement):
        self._evaluate_type()
        value = NIL if xmlelement.get(f'{{{ns.xsi}}}nil') else self._type.parse_xmlelement(xmlelement)
        _list = getattr(instance, field_name)
        _list.append(value)


class ComplexTypeMetaInfo:

    def __init__(self, cls):
        self.cls = cls
        self.fields = []
        self.attributes = []
        self.groups = []
        for attr in dir(cls):
            item = getattr(cls, attr)
            if isinstance(getattr(cls, attr), Attribute):
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
        self.allelements = sorted(self.fields + self.groups, key=lambda f: f._creation_number)
        self.all = sorted(self.fields + self.groups + self.attributes, key=lambda f: f._creation_number)


class Complex_PythonType(type):
    """Python type for ComplexType, builds a _meta object for every class that inherit from ComplexType."""

    def __new__(metacls, name, bases, attrs):
        newcls = super().__new__(metacls, name, bases, attrs)
        if name != 'Complex':
            newcls._meta = ComplexTypeMetaInfo(newcls)
        return newcls


@functools.total_ordering
class ComplexType(Type, metaclass=Complex_PythonType):
    """Parent for XML elements that have sub-elements."""

    INDICATOR = Sequence  # Indicator see: class Indicators. To be defined in sub-type.
    INHERITANCE = None    # Type of inheritance see: class Inheritance, to be defined in sub-type.
    SCHEMA = None

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        for field in instance._meta.all:
            setattr(instance, field._name, field.empty_value())
        return instance

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __setattr__(self, attr, value):
        if attr == '_xmlelement':
            super().__setattr__(attr, value)
        else:
            try:
                field = self._find_field(self._meta.all, attr)
                super().__setattr__(attr, field.accept(value))
            except IndexError as e:
                raise AttributeError(f"Model '{self.__class__.__name__}' doesn't have attribute '{attr}'.") from e

    def __str__(self):
        fields = {f._name: getattr(self, f._name, '<UNKNOWN FIELD>') for f in self._meta.fields}
        fields = ', '.join('%s=%s' % item for item in fields.items())
        return f'<{self.__class__.__name__}: {fields}>'

    def __hash__(self):
        # FIXME: We should do this without the conversion back to XML.
        return hash(etree.tostring(self._xmlelement)) if hasattr(self, '_xmlelement') else id(self)

    def __eq__(self, other):
        # FIXME: We should do this without the conversion back to XML.
        return hasattr(self, '_xmlelement') and hasattr(other, '_xmlelement') \
            and etree.tostring(self._xmlelement) == etree.tostring(other._xmlelement)

    def __lt__(self, other):
        # FIXME: We should do this without the conversion back to XML.
        return hasattr(self, '_xmlelement') and hasattr(other, '_xmlelement') \
            and etree.tostring(self._xmlelement) < etree.tostring(other._xmlelement)

    def accept(self, value):
        """Instance methods that validate other instances."""
        if value is None:
            return None
        elif isinstance(value, self.__class__):
            return value
        else:
            raise ValueError(f'Wrong value object type {value!r} for {self.__class__.__name__}.')

    def render(self, parent, instance, namespace=None, elementFormDefault=None):
        if instance is None:
            return None
        if self.SCHEMA:
            namespace = self.SCHEMA.targetNamespace
        for field in instance._meta.all:
            field.render(
                parent=parent,
                field_name=field.tagname or field._name,
                value=getattr(instance, field._name),
                namespace=namespace,
                elementFormDefault=elementFormDefault)

    @classmethod
    def _find_field(cls, fields, name):
        try:
            return next(f for f in fields if f._name == name)
        except StopIteration:
            pass
        raise ValueError(f"{cls.__name__} has no field '{name}'")

    @classmethod
    def _get_field_by_name(cls, fields, field_name):
        for field in fields:
            if field.tagname == field_name or field._name == field_name:
                return field
        raise ValueError(f"Field not found '{field_name}', fields: {fields}")

    @classmethod
    def _is_matching_element(cls, field, xmlelement):
        def gettagns(tag):
            """Translate a tag string in a format {namespace} tag to a tuple (namespace, tag)."""
            return tag[1:].split('}', 1) if tag[0] == '{' else (None, tag)
        if isinstance(xmlelement, etree._Comment):
            return False
        ns, tag = gettagns(xmlelement.tag)
        return tag == field._name or tag == field.tagname

    @classmethod
    def _find_subelement(cls, field, xmlelement):
        return [subelement for subelement in xmlelement if cls._is_matching_element(field, subelement)]

    @classmethod
    def parse_xmlelement(cls, xmlelement):
        instance = cls()
        instance._xmlelement = xmlelement
        for attribute in instance._meta.attributes:
            attribute.parse(instance, attribute._name, xmlelement)

        is_choice = (instance._meta.cls.INDICATOR == Choice)
        for field in instance._meta.fields:
            if is_choice:
                if not cls._is_matching_element(field, xmlelement):
                    continue
                subelements = [xmlelement]
            else:
                subelements = cls._find_subelement(field, xmlelement)
            for subelement in subelements:
                field.parse(instance, field._name, subelement)
            if is_choice:
                break

        for group in instance._meta.groups:
            group.parse(instance, group._name, xmlelement)

        return instance

    @classmethod
    def __parse_with_validation(cls, xml, schema):
        from .py2xsd import generate_xsd
        schema = generate_xsd(schema)
        schemaelement = etree.XMLSchema(schema)
        if isinstance(xml, str):
            parser = etree.XMLParser(schema=schemaelement)
            xmlelement = etree.fromstring(xml, parser)
        else:
            schemaelement.assertValid(xml)
            xmlelement = xml
        return xmlelement

    @classmethod
    def parsexml(cls, xml, schema=None):
        if schema is None:
            parser = etree.fromstring
        else:
            if not isinstance(schema, etree.XMLSchema):
                from .py2xsd import generate_xsd
                schema = etree.XMLSchema(generate_xsd(schema))
            xmlparser = etree.XMLParser(schema=schema)
            parser = functools.partial(etree.fromstring, parser=xmlparser)
        xmlelement = parser(xml)
        return cls.parse_xmlelement(xmlelement)

    def xml(self, tagname, namespace=None, elementFormDefault=None, schema=None, pretty_print=True):
        if namespace:
            tagname = f'{{{namespace}}}{tagname}'
        xmlelement = etree.Element(tagname)
        self.render(xmlelement, self, namespace, elementFormDefault)
        if schema is not None:
            schema.assertValid(xmlelement)
        return etree.tostring(xmlelement, pretty_print=pretty_print)

    @classmethod
    def _force_elements_type_evalution(cls):
        """Allow a schema object to force elements type evalution for XSD generation."""
        for element in cls._meta.all:
            element._evaluate_type()


class Group(ComplexType):
    """Parent object for XSD Groups. Marker. Must be used with Ref."""


class AttributeGroup(Group):
    """Parent object for XSD Attribute Groups. Marker. Must be used with Ref."""


class Document(ComplexType):
    """Represent the whole xml, is expected to have only one field (root element)."""

    NAMESPACE = None

    class MockElement:
        def __init__(self):
            self.element = None

        def append(self, element):
            self.element = element

    def render(self):
        field = self._meta.fields[0]  # The only field.
        mockelement = Document.MockElement()
        instance = getattr(self, field._name)
        field.render(mockelement, field._name, instance, self.NAMESPACE)
        return etree.tostring(mockelement.element, pretty_print=True)

    # TODO: Add schema support.
    @classmethod
    def parsexml(cls, xml):
        field = cls._meta.fields[0]  # The only field.
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


# TODO: Replace this with xsd.List(xsd.NMTOKEN)
class NMTOKENS(String):
    pass


class AnyType(Type):
    pass


class Base64Binary(String):
    pass


class Duration(String):
    pass


class Schema:
    """
    Main object for XSD schema.

    This object is required for XSD and WSDL generation and needs correct namespaces as it propagates targetNamespace
    to all objects. Instance of this is expected to be named Schema.
    """

    def __init__(self, targetNamespace, elementFormDefault=ElementFormDefault.UNQUALIFIED, simpleTypes=None,
                 attributeGroups=None, groups=None, complexTypes=None, elements=None, imports=None, includes=None,
                 location=None):
        """
        :param targetNamespace: string, xsd namespace URL.
        :param elementFormDefault: unqualified/qualified. Defines if namespaces
            be used in child elements.
            Suggested: qualified. Default: unqualified (same default as in XSD).
        :param simpleTypes: List of objects that extend xsd.SimpleType.
        :param attributeGroups: List of objects that extend xsd.AttributeGroup.
        :param groups: List of objects that extend xsd.Group.
        :param complexTypes: List of complexTypes class.
        :param elements: dict of xsd.Elements that are direct schema elements.
        """
        self.targetNamespace = targetNamespace
        self.elementFormDefault = elementFormDefault
        self.simpleTypes = simpleTypes or []
        self.attributeGroups = attributeGroups or []
        self.groups = groups or []
        self.complexTypes = complexTypes or []
        self.elements = elements or {}
        self.imports = imports or ()
        self.includes = includes or ()
        self.location = location

        self.__init_schema(self.simpleTypes)
        self.__init_schema(self.groups)
        self.__init_schema(self.attributeGroups)
        self.__init_schema(self.complexTypes)

        for element in self.elements.values():
            if isinstance(element._passed_type, ComplexType):
                element._passed_type.__class__.SCHEMA = self
            if element.namespace is None:
                element.namespace = targetNamespace

        self._force_elements_type_evalution(self.complexTypes)
        self._force_elements_type_evalution(self.attributeGroups)
        self._force_elements_type_evalution(self.groups)

        for element in self.elements.values():
            element._evaluate_type()

    def __init_schema(self, types):
        for _type in types:
            _type.SCHEMA = self

    def _force_elements_type_evalution(self, types):
        for t in types:
            t._force_elements_type_evalution()

    def get_element_by_name(self, name):
        if name in self.elements:
            return self.elements[name]

        for i in itertools.chain(self.imports, self.includes):
            element = i.get_element_by_name(name)
            if element is not None:
                return element

        return None


class Method:
    """
    Method description.

    The main information is mapping soapAction and operationName to a function for the dispatcher.
    input and output mapping informs how and which objects should be created on incoming/outgoing messages.
    """

    def __init__(self, operationName, soapAction, input=None, output=None, function=None, inputPartName='body',
                 outputPartName='body', input_header=None, output_header=None, style=CallStyle.DOCUMENT):
        """:param function: The function that should be called. Required only for server implementations."""
        self.operationName = operationName
        self.soapAction = soapAction
        self.input = input
        self.output = output
        self.function = function
        self.inputPartName = inputPartName
        self.outputPartName = outputPartName
        self.input_header = input_header
        self.output_header = output_header
        self.style = style


class NamedType(ComplexType):
    name = Element(String)
    value = Element(ComplexType)

    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value
