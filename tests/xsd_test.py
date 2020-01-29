import decimal
import unittest

import iso8601
from lxml import etree

from soapfish import xsd, xsdspec


class Aircraft(xsd.ComplexType):
    tail_number = xsd.Attribute(xsd.String)


class Airport(xsd.ComplexType):
    type = xsd.Element(xsd.String)
    code = xsd.Element(xsd.String)

    @classmethod
    def create(cls, type, code):
        airport = Airport()
        airport.type = type
        airport.code = code
        return airport


class Pilot(xsd.String):
    enumeration = ['CAPTAIN', 'FIRST_OFFICER']


class Flight(xsd.ComplexType):
    tail_number = xsd.Element(xsd.String)
    takeoff_datetime = xsd.Element(xsd.DateTime, minOccurs=0)
    takeoff_airport = xsd.Element(Airport)
    landing_airport = xsd.Element(Airport)
    takeoff_pilot = xsd.Element(Pilot, minOccurs=0)
    landing_pilot = xsd.Element(Pilot, minOccurs=0)
    passengers = xsd.ListElement(xsd.String, 'passenger', maxOccurs=10, minOccurs=0)


class ElementTest(unittest.TestCase):
    # This logic have been moved to post rendering validation uncomment when implemented.
    # def test_required(self):
    #     tail_number = xsd.Element(xsd.String)
    #     try:
    #         xmlelement = etree.Element('aircraft')
    #         tail_number.render(xmlelement, 'tail_number', None)
    #     except ValueError:
    #         pass
    #     else:
    #         raise AssertionError('Should get here')

    def test_string_element(self):
        tail_number = xsd.Element(xsd.String())
        xmlelement = etree.Element('aircraft')
        tail_number.render(xmlelement, 'tail_number', 'LN-KKU')
        self.assertEqual(b'''<aircraft>
  <tail_number>LN-KKU</tail_number>
</aircraft>
''',
                         etree.tostring(xmlelement, pretty_print=True))

    def test_complex_type_element(self):
        airport = Airport()
        airport.type = 'IATA'
        airport.code = 'WAW'
        xmlelement = etree.Element('takeoff_airport')
        airport.render(xmlelement, airport)
        expected_xml = b'''<takeoff_airport>
  <type>IATA</type>
  <code>WAW</code>
</takeoff_airport>
'''
        xml = etree.tostring(xmlelement, pretty_print=True)
        self.assertEqual(expected_xml, xml)

    def test_tagname_parsexml(self):
        class TestType(xsd.ComplexType):
            foo = xsd.Element(xsd.String, tagname='bar')
        xml = b'<T><bar>coucou</bar></T>'
        obj = TestType.parsexml(xml)
        self.assertEqual('coucou', obj.foo)

    def test_tagname_parse_xmlelement(self):
        class TestType(xsd.ComplexType):
            foo = xsd.Element(xsd.String, tagname='bar')
        xml = b'<T><bar>coucou</bar></T>'
        xmlelement = etree.fromstring(xml)
        obj = TestType.parse_xmlelement(xmlelement)
        self.assertEqual('coucou', obj.foo)

    def test_tagname_render(self):
        class TestType(xsd.ComplexType):
            foo = xsd.Element(xsd.String, tagname='bar')
        obj = TestType(foo='coucou')
        xmlelement = etree.Element('T')
        obj.render(xmlelement, obj)
        xml = etree.tostring(xmlelement)
        self.assertEqual(b'<T><bar>coucou</bar></T>', xml)

    def test_stringify_complextype(self):
        flight = Flight(takeoff_airport=Airport())
        str(flight)


class ListElementTest(unittest.TestCase):

    def test_rendering_simple_type(self):
        passengers = xsd.ListElement(xsd.String, 'passenger', maxOccurs=10, minOccurs=0)
        passengers_list = ['abc', '123']
        xmlelement = etree.Element('flight')
        passengers.render(xmlelement, 'passenger', passengers_list)
        expected_xml = b'''<flight>
  <passenger>abc</passenger>
  <passenger>123</passenger>
</flight>
'''
        xml = etree.tostring(xmlelement, pretty_print=True)
        self.assertEqual(expected_xml, xml)

    def test_parsing(self):
        class Test(xsd.ComplexType):
            values = xsd.ListElement(xsd.Int, 'value')
        XML = b'''
        <test>
            <value>1</value>
            <value>2</value>
        </test>'''
        test = Test.parsexml(XML)
        self.assertEqual(2, len(test.values))
        self.assertEqual(1, test.values[0])

    def test_append_restriction(self):
        x = xsd.ListElement(xsd.String, maxOccurs=1, tagname='toto').empty_value()
        x.append('a')
        with self.assertRaises(ValueError) as cm:
            x.append('a')
        self.assertEqual('You must not add more than 1 items to this list.', str(cm.exception))

    def test_append_with_max_occurs_unbounded(self):
        x = xsd.ListElement(xsd.String, maxOccurs=xsd.UNBOUNDED, tagname='toto').empty_value()
        x.append('a')
        x.append('a')


class BooleanTypeTest(unittest.TestCase):

    def test_element_true(self):
        mixed = xsd.Element(xsd.Boolean)
        xmlelement = etree.Element('complexType')
        mixed.render(xmlelement, 'mixed', True)
        expected_xml = b'''<complexType>
  <mixed>true</mixed>
</complexType>
'''
        xml = etree.tostring(xmlelement, pretty_print=True)
        self.assertEqual(expected_xml, xml)

    def test_boolean_correctly_renders_false_value_in_xml(self):
        # regression test for http://code.google.com/p/soapfish/issues/detail?id=3
        # before xsd.Boolean would render [true, false] Python values *both*
        # to as 'true' in the xml.
        parent = etree.Element('parent')
        xsd.Element(xsd.Boolean).render(parent, 'b', True)
        self.assertEqual(b'<parent><b>true</b></parent>', etree.tostring(parent))

        parent = etree.Element('parent')
        xsd.Element(xsd.Boolean).render(parent, 'b', False)
        self.assertEqual(b'<parent><b>false</b></parent>', etree.tostring(parent))

    def test_attribute_false(self):
        mixed = xsd.Attribute(xsd.Boolean)
        xmlelement = etree.Element('complexType')
        mixed.render(xmlelement, 'mixed', True)
        expected_xml = b'<complexType mixed="true"/>\n'
        xml = etree.tostring(xmlelement, pretty_print=True)
        self.assertEqual(expected_xml, xml)

    def test_attribute_nil(self):
        mixed = xsd.Attribute(xsd.Boolean, nillable=True, use=xsd.Use.OPTIONAL)
        xmlelement = etree.Element('complexType')
        mixed.render(xmlelement, 'mixed', xsd.NIL)
        expected_xml = b'<complexType mixed="nil"/>\n'
        xml = etree.tostring(xmlelement, pretty_print=True)
        self.assertEqual(expected_xml, xml)


class DecimalTypeTest(unittest.TestCase):

    def test_python_decimal(self):

        class Test(xsd.ComplexType):
            float = xsd.Element(xsd.Decimal())

        test = Test()
        test.float = decimal.Decimal('2.2')

    def test_enumeration(self):

        class Test(xsd.ComplexType):
            integer = xsd.Element(xsd.Decimal(enumeration=[1, 2, 3]))

        test = Test()
        try:
            test.integer = 4
        except ValueError:
            pass
        else:
            self.fail('Should not get here.')

    def test_fractionDigits(self):

        class Test(xsd.ComplexType):
            float = xsd.Element(xsd.Decimal(fractionDigits=2))

        test = Test()
        test.float = 2.22
        try:
            test.float = 2.2
        except ValueError:
            pass
        else:
            self.fail('Should not get here.')

    def test_Inclusive(self):

        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.Decimal(minInclusive=0, maxInclusive=100))

        test = Test()
        test.value = 0
        test.value = 50
        test.value = 100
        try:
            test.value = -1
        except ValueError:
            pass
        else:
            self.fail('Should not get here.')
        try:
            test.value = 101
        except ValueError:
            pass
        else:
            self.fail('Should not get here.')

    def test_Exclusive(self):

        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.Decimal(minExclusive=-100, maxExclusive=0))

        test = Test()
        test.value = -99
        test.value = -50
        test.value = -1
        try:
            test.value = -100
        except ValueError:
            pass
        else:
            self.fail('Should not get here.')
        try:
            test.value = 0
        except ValueError:
            pass
        else:
            self.fail('Should not get here.')
        try:
            test.value = 1
        except ValueError:
            pass
        else:
            self.fail('Should not get here.')
        try:
            test.value = -101
        except ValueError:
            pass
        else:
            self.fail('Should not get here.')

    def test_pattern(self):

        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.Decimal(pattern=r'1+'))

        test = Test()
        test.value = 11
        test.value = 111
        try:
            test.value = 2
        except ValueError:
            pass
        else:
            self.fail('Should not get here.')

    def test_totalDigits(self):

        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.Decimal(totalDigits=4))

        test = Test()
        test.value = 1.2
        test.value = 22.22
        test.value = 1.234
        try:
            test.value = 12.345
        except ValueError:
            pass
        else:
            self.fail('Should not get here.')
        try:
            test.value = 12345
        except ValueError:
            pass
        else:
            self.fail('Should not get here.')

    def test_rendring(self):

        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.Decimal)

        test = Test()
        test.value = 4.13
        xml = test.xml('test')
        self.assertEqual(b'<test>\n  <value>4.13</value>\n</test>\n', xml)

    def test_parsing(self):
        xml = b'<test><value>3.14</value></test>'

        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.Decimal)

        test = Test.parsexml(xml)
        self.assertEqual(test.value, 3.14, 'PI value is wrong OMG!')


class IntegerTypeTest(unittest.TestCase):

    def test_rendering_and_parsing(self):
        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.Integer(totalDigits=2))
        test = Test()
        test.value = 22
        xml = test.xml('test')
        XML = b'<test>\n  <value>22</value>\n</test>\n'
        self.assertEqual(XML, xml)

        test1 = Test.parsexml(XML)
        self.assertEqual(22, test1.value)

    def test_Int(self):
        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.Int)
        test = Test()
        test.value = 1
        self.assertEqual(1, test.value)
        try:
            test.value = 2147483648
        except ValueError:
            pass
        else:
            self.fail('Should not get here.')

        try:
            test.value = -2147483649
        except ValueError:
            pass
        else:
            self.fail('Should not get here.')

    def test_Long(self):

        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.Long)

        test = Test()
        test.value = 1
        self.assertEqual(1, test.value)
        try:
            test.value = 9223372036854775807 + 1
        except ValueError:
            pass
        else:
            self.fail('Should not get here.')
        try:
            test.value = -9223372036854775808 - 1
        except ValueError:
            pass
        else:
            self.fail('Should not get here.')


class ComplexTest(unittest.TestCase):

    def test_rendering(self):
        airport = Airport()
        airport.type = 'IATA'
        airport.code = 'WAW'
        xmlelement = etree.Element('airport')
        airport.render(xmlelement, airport)
        xml = etree.tostring(xmlelement, pretty_print=True)
        expected_xml = b'''<airport>
  <type>IATA</type>
  <code>WAW</code>
</airport>
'''
        self.assertEqual(expected_xml, xml)

    def test_attribute_rendering(self):
        aircraft = Aircraft()
        aircraft.tail_number = 'LN-KKX'
        xmlelement = etree.Element('aircraft')
        aircraft.render(xmlelement, aircraft)
        expected_xml = b'<aircraft tail_number="LN-KKX"/>\n'
        xml = etree.tostring(xmlelement, pretty_print=True)
        self.assertEqual(expected_xml, xml)

    def test_attribute_parsing(self):
        XML = b'<aircraft tail_number="LN-KKX"/>\n'
        aircraft = Aircraft.parsexml(XML)
        self.assertEqual('LN-KKX', aircraft.tail_number)

    def test_multilayer_complex(self):
        flight = Flight()
        flight.tail_number = 'LN-KKA'
        flight.takeoff_airport = Airport.create('IATA', 'WAW')
        flight.landing_airport = Airport.create('ICAO', 'EGLL')

        try:
            flight.takeoff_pilot = 'ABC'
        except ValueError:
            pass
        else:
            self.fail()
        flight.takeoff_pilot = 'CAPTAIN'

        xmlelement = etree.Element('flight')
        flight.render(xmlelement, flight)
        xml = etree.tostring(xmlelement, pretty_print=True)
        expected_xml = b'''<flight>
  <tail_number>LN-KKA</tail_number>
  <takeoff_airport>
    <type>IATA</type>
    <code>WAW</code>
  </takeoff_airport>
  <landing_airport>
    <type>ICAO</type>
    <code>EGLL</code>
  </landing_airport>
  <takeoff_pilot>CAPTAIN</takeoff_pilot>
</flight>
'''
        self.assertEqual(expected_xml, xml)

    def test_complex_with_list(self):
        flight = Flight()
        flight.tail_number = 'LN-KKA'
        flight.takeoff_airport = Airport.create('IATA', 'WAW')
        flight.landing_airport = Airport.create('ICAO', 'EGLL')
        flight.passengers.append('abc')
        flight.passengers.append('123')

        xmlelement = etree.Element('flight')
        flight.render(xmlelement, flight)
        xml = etree.tostring(xmlelement, pretty_print=True)
        expected_xml = b'''<flight>
  <tail_number>LN-KKA</tail_number>
  <takeoff_airport>
    <type>IATA</type>
    <code>WAW</code>
  </takeoff_airport>
  <landing_airport>
    <type>ICAO</type>
    <code>EGLL</code>
  </landing_airport>
  <passenger>abc</passenger>
  <passenger>123</passenger>
</flight>
'''
        self.assertEqual(expected_xml, xml)

    def test_inheritance_rendering(self):

        class A(xsd.ComplexType):
            name = xsd.Attribute(xsd.String)

        class B(A):
            type = xsd.Attribute(xsd.String)

        b = B()
        b.name = 'b'
        b.type = 'B'
        xml = b.xml('inheritance')
        EXPECTED_XML = b'<inheritance name="b" type="B"/>\n'
        self.assertEqual(EXPECTED_XML, xml)

    def test_inheritance_parsing(self):

        class A(xsd.ComplexType):
            name = xsd.Attribute(xsd.String)

        class B(A):
            type = xsd.Element(xsd.String)

        XML = b'''<inheritance name="b">
  <type>B</type>
</inheritance>\n'''
        b = B.parsexml(XML)
        self.assertEqual(b.name, 'b')
        self.assertEqual(b.type, 'B')

    def test_parsexml_with_soapfish_schema(self):
        # sometimes it comes handy that soapfish can validate some XML against a
        # provided soapfish schema (instead of an etree.XMLSchema) especially in
        # testing.
        class A(xsd.ComplexType):
            name = xsd.Element(xsd.String, nillable=True)
        ns = 'http://foo.example'
        soapfish_schema = xsd.Schema(ns,
                                     imports=[],
                                     elementFormDefault=xsd.ElementFormDefault.UNQUALIFIED,
                                     simpleTypes=[],
                                     attributeGroups=[],
                                     groups=[],
                                     complexTypes=[A],
                                     elements={'foo': xsd.Element(A)},
                                     )
        xml = '<test:foo xmlns:test="%s"><name>bar</name></test:foo>' % ns
        foo = A.parsexml(xml, schema=soapfish_schema)
        self.assertEqual('bar', foo.name)


class XMLParsingTest(unittest.TestCase):
    SIMPLE_XML = b'''<flight>
  <landing_airport>
    <code>EGLL</code>
    <type>ICAO</type>
  </landing_airport>
  <tail_number>LN-KKA</tail_number>
  <takeoff_datetime>2001-10-26T21:32:52</takeoff_datetime>
  <takeoff_airport>
    <code>WAW</code>
    <type>IATA</type>
  </takeoff_airport>
</flight>
'''

    def test_simple_parsing(self):
        flight = Flight.parse_xmlelement(etree.fromstring(self.SIMPLE_XML))
        self.assertEqual('LN-KKA', flight.tail_number)
        self.assertEqual('WAW', flight.takeoff_airport.code)
        self.assertEqual('IATA', flight.takeoff_airport.type)
        self.assertEqual('EGLL', flight.landing_airport.code)
        self.assertEqual('ICAO', flight.landing_airport.type)
        self.assertEqual(iso8601.parse_date('2001-10-26T21:32:52Z'), flight.takeoff_datetime)

    LIST_XML = b'''<flight>
  <landing_airport>
    <code>EGLL</code>
    <type>ICAO</type>
  </landing_airport>
  <passenger>abc</passenger>
  <passenger>123</passenger>
  <tail_number>LN-KKA</tail_number>
  <takeoff_airport>
    <code>WAW</code>
    <type>IATA</type>
  </takeoff_airport>
</flight>
'''

    def test_list_parsing(self):
        flight = Flight.parse_xmlelement(etree.fromstring(self.LIST_XML))
        self.assertEqual('LN-KKA', flight.tail_number)
        self.assertEqual('WAW', flight.takeoff_airport.code)
        self.assertEqual('IATA', flight.takeoff_airport.type)
        self.assertEqual('EGLL', flight.landing_airport.code)
        self.assertEqual('ICAO', flight.landing_airport.type)
        self.assertEqual(['abc', '123'], flight.passengers)


class XSD_Spec_Test(unittest.TestCase):
    AIRPORT_XML = '''
    <xs:complexType name="airport" xmlns:xs="http://www.w3.org/2001/XMLSchema">
        <xs:sequence>
            <xs:element name="code_type">
                <xs:simpleType>
                    <xs:restriction base="xs:string">
                        <xs:enumeration value="ICAO"/>
                        <xs:enumeration value="IATA"/>
                        <xs:enumeration value="FAA"/>
                    </xs:restriction>
                </xs:simpleType>
            </xs:element>
            <xs:element name="code" type="xs:string"/>
        </xs:sequence>
    </xs:complexType>'''

    def test_complexType(self):
        airport = xsdspec.XSDComplexType.parse_xmlelement(etree.fromstring(self.AIRPORT_XML))
        self.assertEqual('airport', airport.name)
        code_type_element = airport.sequence.elements[0]
        code_element = airport.sequence.elements[1]
        self.assertEqual('code_type', code_type_element.name)
        self.assertEqual('xs:string', code_type_element.simpleType.restriction.base)
        self.assertEqual(3, len(code_type_element.simpleType.restriction.enumerations))
        self.assertEqual('ICAO', code_type_element.simpleType.restriction.enumerations[0].value)
        self.assertEqual('code', code_element.name)


SCHEMA_XML = '''
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" targetNamespace="http://flightdataservices.com/ops.xsd">
    <xs:complexType name="airport">
        <xs:sequence>
            <xs:element name="code_type">
                <xs:simpleType>
                    <xs:restriction base="xs:string">
                        <xs:enumeration value="ICAO"/>
                        <xs:enumeration value="IATA"/>
                        <xs:enumeration value="FAA"/>
                    </xs:restriction>
                </xs:simpleType>
            </xs:element>
            <xs:element name="code" type="xs:string"/>
        </xs:sequence>
    </xs:complexType>

    <xs:complexType name="weight">
            <xs:sequence>
                <xs:element name="value" type="xs:integer"/>
                <xs:element name="unit">
                    <xs:simpleType>
                        <xs:restriction base="xs:string">
                            <xs:enumeration value="kg"/>
                            <xs:enumeration value="lb"/>
                        </xs:restriction>
                </xs:simpleType>
                </xs:element>
            </xs:sequence>
    </xs:complexType>

    <xs:simpleType name="pilot">
        <xs:restriction base="xs:string">
            <xs:enumeration value="CAPTAIN"/>
            <xs:enumeration value="FIRST_OFFICER"/>
        </xs:restriction>
    </xs:simpleType>
    <xs:complexType name="ops">
        <xs:sequence>
            <xs:element name="aircraft" type="xs:string"/>
            <xs:element name="flight_number" type="xs:string"/>
            <xs:element name="type">
                <xs:simpleType>
                    <xs:restriction base="xs:string">
                        <xs:enumeration value="COMMERCIAL"/>
                        <xs:enumeration value="INCOMPLETE"/>
                        <xs:enumeration value="ENGINE_RUN_UP"/>
                        <xs:enumeration value="TEST"/>
                        <xs:enumeration value="TRAINING"/>
                        <xs:enumeration value="FERRY"/>
                        <xs:enumeration value="POSITIONING"/>
                        <xs:enumeration value="LINE_TRAINING"/>
                    </xs:restriction>
                </xs:simpleType>
            </xs:element>
            <xs:element name="takeoff_airport" type="fds:airport"/>
            <xs:element name="takeoff_gate_datetime" type="xs:dateTime" minOccurs="0"/>
            <xs:element name="takeoff_datetime" type="xs:dateTime"/>
            <xs:element name="takeoff_fuel" minOccurs="0" type="fds:weight"/>
            <xs:element name="takeoff_gross_weight" minOccurs="0" type="fds:weight"/>
            <xs:element name="takeoff_pilot" minOccurs="0" type="fds:pilot"/>
            <xs:element name="landing_airport" type="fds:airport"/>
            <xs:element name="landing_gate_datetime" type="xs:dateTime" minOccurs="0"/>
            <xs:element name="landing_datetime" type="xs:dateTime"/>
            <xs:element name="landing_fuel" minOccurs="0" type="fds:weight"/>
            <xs:element name="landing_pilot" minOccurs="0" type="fds:pilot"/>
            <xs:element name="destination_airport" minOccurs="0" type="fds:airport"/>
            <xs:element name="captain_code" minOccurs="0" type="xs:string"/>
            <xs:element name="first_officer_code" minOccurs="0" type="xs:string"/>
        </xs:sequence>
    </xs:complexType>
    <xs:complexType name="status">
        <xs:sequence>
            <xs:element name="action">
                <xs:simpleType>
                    <xs:restriction base="xs:string">
                        <xs:enumeration value="INSERTED"/>
                        <xs:enumeration value="UPDATED"/>
                        <xs:enumeration value="EXISTS"/>
                    </xs:restriction>
                </xs:simpleType>
            </xs:element>
            <xs:element name="id" type="xs:long"/>
        </xs:sequence>
    </xs:complexType>
    <xs:element name="ops" type="fds:ops"/>
    <xs:element name="status" type="fds:status"/>
</xs:schema>'''


class SchemaTest(unittest.TestCase):
    def test_schema_parsing(self):
        schema = xsdspec.Schema.parse_xmlelement(etree.fromstring(SCHEMA_XML))
        self.assertEqual(4, len(schema.complexTypes))
        self.assertEqual(1, len(schema.simpleTypes))
        self.assertEqual(2, len(schema.elements))

        self.assertEqual('ops', schema.elements[0].name)
        self.assertEqual('fds:ops', schema.elements[0].type)

        ops_type = schema.complexTypes[2]
        self.assertEqual('ops', ops_type.name)
        self.assertEqual('aircraft', ops_type.sequence.elements[0].name)
        self.assertEqual('xs:string', ops_type.sequence.elements[0].type)


class RequestResponseOperation(xsd.Group):
    input = xsd.Element(xsd.String, minOccurs=0)
    output = xsd.Element(xsd.String, minOccurs=0)


class Operation(xsd.ComplexType):
    name = xsd.Element(xsd.String)
    requestResponseOperation = xsd.Ref(RequestResponseOperation)


class GroupTest(unittest.TestCase):
    XML = b'''<operation>
  <name>TEST-Operation</name>
  <input>IN</input>
  <output>OUT</output>
</operation>\n'''

    def test_rendering(self):
        operation = Operation()
        operation.name = 'TEST-Operation'
        operation.requestResponseOperation.input = 'IN'
        operation.requestResponseOperation.output = 'OUT'
        xml = operation.xml('operation')
        self.assertEqual(self.XML, xml)

    def test_parsing(self):
        operation = Operation.parsexml(self.XML)
        self.assertEqual(operation.name, 'TEST-Operation')
        self.assertEqual(operation.requestResponseOperation.input, 'IN')
        self.assertEqual(operation.requestResponseOperation.output, 'OUT')

    def test_rendering_empty_group(self):
        operation = Operation()
        operation.name = 'TEST-Operation'
        xml = operation.xml('operation')
        expected_xml = b'''<operation>
  <name>TEST-Operation</name>
</operation>\n'''
        self.assertEqual(expected_xml, xml)


# <xs:attributeGroup name="tHeaderAttributes">
#   <xs:attribute name="message" type="xs:QName" use="required"/>
#   <xs:attribute name="part" type="xs:NMTOKEN" use="required"/>
#   <xs:attribute name="use" type="soap:useChoice" use="required"/>
#   <xs:attribute name="encodingStyle" type="soap:encodingStyle" use="optional"/>
#   <xs:attribute name="namespace" type="xs:anyURI" use="optional"/>
# </xs:attributeGroup>
class TBodyAttributes(xsd.AttributeGroup):
    encodingStyle = xsd.Attribute(xsd.String, use=xsd.Use.OPTIONAL)
    use = xsd.Attribute(xsd.String)
    namespace = xsd.Attribute(xsd.String)


class TBody(xsd.ComplexType):
    parts = xsd.Attribute(xsd.String)
    tBodyAttributes = xsd.Ref(TBodyAttributes)


class AttributeGroupTest(unittest.TestCase):

    def test_rendering(self):
        body = TBody()
        body.parts = 'Parts'
        body.tBodyAttributes.use = 'required'
        body.tBodyAttributes.namespace = 'xs'
        expected_xml = b'<body parts="Parts" use="required" namespace="xs"/>\n'
        xml = body.xml('body')
        self.assertEqual(expected_xml, xml)

    def test_parsing(self):
        xml = b'<body parts="Parts" use="required" namespace="xs"/>\n'
        body = TBody.parsexml(xml)
        self.assertEqual(body.parts, 'Parts')
        self.assertEqual(body.tBodyAttributes.use, 'required')
        self.assertEqual(body.tBodyAttributes.namespace, 'xs')
        self.assertIsNone(body.tBodyAttributes.encodingStyle)


class AirporttDocument(xsd.Document):
    airport = xsd.Element(Airport)


class DocumentTest(unittest.TestCase):

    def test_document_rendering(self):
        document = AirporttDocument()
        document.airport = Airport(code='XXX', type='IATA')
        xml = document.render()
        expected_xml = b'''<airport>
  <type>IATA</type>
  <code>XXX</code>
</airport>\n'''
        self.assertEqual(xml, expected_xml)


class NillableTest(unittest.TestCase):

    def test_nilable_element_rendering(self):

        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.Integer, nillable=True)
            notnillable = xsd.Element(xsd.Integer, minOccurs=0)

        test = Test()
        test.value = xsd.NIL
        xml = test.xml('test')
        EXPECTED_XML = b'''<test>
  <value xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
</test>\n'''
        self.assertEqual(xml, EXPECTED_XML)
        try:
            test.notnillable = xsd.NIL
        except ValueError:
            pass
        else:
            self.fail('Should not get here.')

    def test_nillable_element_parsing(self):

        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.Long, nillable=True)

        xml = b'<test><value xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/></test>'
        test = Test.parsexml(xml)
        self.assertEqual(test.value, xsd.NIL)

    def test_nillable_list_rendering(self):

        class Test(xsd.ComplexType):
            values = xsd.ListElement(xsd.String, 'value', nillable=True)
            notnillable = xsd.ListElement(xsd.String, 'notnillable', minOccurs=0)

        test = Test()
        test.values.append('XXX')
        test.values.append(xsd.NIL)
        xml = test.xml('test')
        EXPECTED_XML = b'''<test>
  <value>XXX</value>
  <value xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
</test>\n'''
        self.assertEqual(xml, EXPECTED_XML)

        self.assertRaises(Exception, lambda: test.notnillable.append(xsd.NIL))

    def test_nillable_list_parsing(self):

        class Test(xsd.ComplexType):
            values = xsd.ListElement(xsd.Int, 'value', nillable=True)

        XML = b'''<test>
                    <value>1</value>
                    <value xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
                    <value xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
                    <value>2</value>
                </test>
                '''
        test = Test.parsexml(XML)
        self.assertEqual(test.values[0], 1)
        self.assertEqual(test.values[1], xsd.NIL)
        self.assertEqual(test.values[2], xsd.NIL)
        self.assertEqual(test.values[3], 2)

    def test_nillable_attribute(self):

        class Test(xsd.ComplexType):
            value = xsd.Attribute(xsd.String, nillable=True, use=xsd.Use.OPTIONAL)

        test = Test()
        self.assertEqual(test.xml('test'), b'<test/>\n')
        test.value = xsd.NIL
        self.assertEqual(b'<test value="nil"/>\n', test.xml('test'))


class ElementTypeEvaluation(unittest.TestCase):

    def test_string_type_evalutation(self):

        class B1(xsd.ComplexType):
            a = xsd.Element('soapfish.xsd.String')
            b = xsd.Element('soapfish.xsd.Integer')

        b = B1()
        b.a = 'test'
        b.b = 123


class PatternTest(unittest.TestCase):

    def test_string_pattern(self):

        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.String(pattern=r'^a*$'))

        test = Test()
        test.value = 'a'
        test.value = 'aaa'
        try:
            test.value = 'b'
        except ValueError:
            pass
        else:
            self.fail('Should not get here.')


class MaxOccursTest(unittest.TestCase):

    def test_xmlvalue_simple(self):
        max_occurs = xsd.MaxOccurs()
        value = max_occurs.xmlvalue(1)
        self.assertEqual('1', value)
        value = max_occurs.xmlvalue(5)
        self.assertEqual('5', value)

    def test_xmlvalue_unbounded(self):
        max_occurs = xsd.MaxOccurs()
        value = max_occurs.xmlvalue(xsd.UNBOUNDED)
        self.assertEqual('unbounded', value)

    def test_pythonvalue_simple(self):
        max_occurs = xsd.MaxOccurs()
        value = max_occurs.pythonvalue('1')
        self.assertEqual(1, value)
        value = max_occurs.pythonvalue('5')
        self.assertEqual(5, value)

    def test_pythonvalue_unbounded(self):
        max_occurs = xsd.MaxOccurs()
        value = max_occurs.pythonvalue('unbounded')
        self.assertEqual(xsd.UNBOUNDED, value)
