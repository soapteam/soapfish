import unittest
from datetime import datetime
from lxml import etree
from soapbox import xsd, xsdspec
from soapbox import iso8601


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
    enumeration = ["CAPTAIN", "FIRST_OFFICER"]


class Flight(xsd.ComplexType):
    tail_number = xsd.Element(xsd.String)
    takeoff_datetime = xsd.Element(xsd.DateTime, minOccurs=0)
    takeoff_airport = xsd.Element(Airport)
    landing_airport = xsd.Element(Airport)
    takeoff_pilot = xsd.Element(Pilot, minOccurs=0)
    landing_pilot = xsd.Element(Pilot, minOccurs=0)
    passangers = xsd.ListElement(xsd.String, "passanger", maxOccurs=10, minOccurs=0)


class ElementTest(unittest.TestCase):
# This logic have been moved to post rendering validation
# uncomment when implemented.
#    def test_required(self):
#        tail_number = xsd.Element(xsd.String)
#        try:
#            xmlelement = etree.Element("aircraft")
#            tail_number.render(xmlelement, "tail_number", None)
#        except ValueError:
#            pass
#        else:
#            raise AssertionError("Should get here")

    def test_string_element(self):
        tail_number = xsd.Element(xsd.String())
        xmlelement = etree.Element("aircraft")
        tail_number.render(xmlelement, "tail_number", "LN-KKU")
        self.assertEqual("""<aircraft>
  <tail_number>LN-KKU</tail_number>
</aircraft>
""",
                         etree.tostring(xmlelement, pretty_print=True))

    def test_complex_type_element(self):
        airport = Airport()
        airport.type = "IATA"
        airport.code = "WAW"
        xmlelement = etree.Element("takeoff_airport")
        airport.render(xmlelement, airport)
        expected_xml = """<takeoff_airport>
  <type>IATA</type>
  <code>WAW</code>
</takeoff_airport>
"""
        xml = etree.tostring(xmlelement, pretty_print=True)
        self.assertEqual(expected_xml, xml)


class ListElementTest(unittest.TestCase):

    def test_rendering_simple_type(self):
        passangers = xsd.ListElement(xsd.String, "passanger", maxOccurs=10, minOccurs=0)
        passangers_list = ["abc", "123"]
        xmlelement = etree.Element("flight")
        passangers.render(xmlelement, "passanger", passangers_list)
        expected_xml = """<flight>
  <passanger>abc</passanger>
  <passanger>123</passanger>
</flight>
"""
        xml = etree.tostring(xmlelement, pretty_print=True)
        self.assertEqual(expected_xml, xml)

    def test_parsing(self):
        class Test(xsd.ComplexType):
            values = xsd.ListElement(xsd.Int, "value")
        XML = """
        <test>
            <value>1</value>
            <value>2</value>
        </test>"""
        test = Test.parsexml(XML)
        self.assertEqual(2, len(test.values))
        self.assertEqual(1, test.values[0])


class BooleanTypeTest(unittest.TestCase):

    def test_element_true(self):
        mixed = xsd.Element(xsd.Boolean,)
        xmlelement = etree.Element("complexType")
        mixed.render(xmlelement, "mixed", True)
        expected_xml = """<complexType>
  <mixed>true</mixed>
</complexType>
"""
        xml = etree.tostring(xmlelement, pretty_print=True)
        self.assertEqual(expected_xml, xml)

    def test_attribute_false(self):
        mixed = xsd.Attribute(xsd.Boolean)
        xmlelement = etree.Element("complexType")
        mixed.render(xmlelement, "mixed", True)
        expected_xml = """<complexType mixed="true"/>\n"""
        xml = etree.tostring(xmlelement, pretty_print=True)
        self.assertEqual(expected_xml, xml)

    def test_attribute_nil(self):
        mixed = xsd.Attribute(xsd.Boolean, nillable=True, use=xsd.Use.OPTIONAL)
        xmlelement = etree.Element("complexType")
        mixed.render(xmlelement, "mixed", xsd.NIL)
        expected_xml = """<complexType mixed="nil"/>\n"""
        xml = etree.tostring(xmlelement, pretty_print=True)
        self.assertEqual(expected_xml, xml)


class DecimalTypeTest(unittest.TestCase):

    def test_enumeration(self):

        class Test(xsd.ComplexType):
            integer = xsd.Element(xsd.Decimal(enumeration=[1, 2, 3]))

        test = Test()
        try:
            test.integer = 4
        except ValueError:
            pass
        else:
            self.assertTrue(False, "Should not get here.")

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
            self.assertTrue(False, "Should not get here.")

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
            self.assertTrue(False, "Should not get here.")
        try:
            test.value = 101
        except ValueError:
            pass
        else:
            self.assertTrue(False, "Should not get here.")

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
            self.assertTrue(False, "Should not get here.")
        try:
            test.value = 0
        except ValueError:
            pass
        else:
            self.assertTrue(False, "Should not get here.")
        try:
            test.value = 1
        except ValueError:
            pass
        else:
            self.assertTrue(False, "Should not get here.")
        try:
            test.value = -101
        except ValueError:
            pass
        else:
            self.assertTrue(False, "Should not get here.")

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
            self.assertTrue(False, "Should not get here.")

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
            self.assertTrue(False, "Should not get here.")
        try:
            test.value = 12345
        except ValueError:
            pass
        else:
            self.assertTrue(False, "Should not get here.")

    def test_rendring(self):

        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.Decimal)

        test = Test()
        test.value = 4.13
        xml = test.xml("test")
        self.assertEqual("<test>\n  <value>4.13</value>\n</test>\n", xml)

    def test_parsing(self):
        xml = "<test><value>3.14</value></test>"

        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.Decimal)

        test = Test.parsexml(xml)
        self.assertEqual(test.value, 3.14, "PI value is wrong OMG!")


class IntegerTypeTest(unittest.TestCase):

    def test_rendering_and_parsing(self):
        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.Integer(totalDigits=2))
        test = Test()
        test.value = 22
        xml = test.xml("test")
        XML = "<test>\n  <value>22</value>\n</test>\n"
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
            self.assertTrue(False, "Should not get here.")

        try:
            test.value = -2147483649
        except ValueError:
            pass
        else:
            self.assertTrue(False, "Should not get here.")

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
            self.assertTrue(False, "Should not get here.")
        try:
            test.value = -9223372036854775808 - 1
        except ValueError:
            pass
        else:
            self.assertTrue(False, "Should not get here.")


class DatetimeTest(unittest.TestCase):

    def test_rendering(self):
        dt = datetime(2001, 10, 26, 21, 32, 52)
        mixed = xsd.Element(xsd.DateTime)
        xmlelement = etree.Element("flight")
        mixed.render(xmlelement, "takeoff_datetime", dt)
        expected_xml = """<flight>
  <takeoff_datetime>2001-10-26T21:32:52</takeoff_datetime>
</flight>
"""
        xml = etree.tostring(xmlelement, pretty_print=True)
        self.assertEqual(expected_xml, xml)

    def test_wrong_type(self):
        mixed = xsd.Element(xsd.DateTime)
        xmlelement = etree.Element("flight")
        try:
            mixed.render(xmlelement, "takeoff_datetime", 1)
        except Exception:
            pass
        else:
            self.assertTrue(False)

    def test_parsing_utctimezone(self):
        class Test(xsd.ComplexType):
            datetime = xsd.Element(xsd.DateTime)
        XML = """<root><datetime>2011-06-30T00:19:00+0000Z</datetime></root>"""
        test = Test.parsexml(XML)
        self.assertEqual(datetime(2011, 6, 30, 0, 19, 0), test.datetime.replace(tzinfo=None))

    def test_parsing_timezone(self):
        class Test(xsd.ComplexType):
            datetime = xsd.Element(xsd.DateTime)
        XML = """<root><datetime>2011-06-30T20:19:00+01:00</datetime></root>"""
        test = Test.parsexml(XML)
        self.assertEqual(datetime(2011, 6, 30, 19, 19, 0), test.datetime.astimezone(iso8601.UTC).replace(tzinfo=None))


class ComplexTest(unittest.TestCase):

    def test_rendering(self):
        airport = Airport()
        airport.type = "IATA"
        airport.code = "WAW"
        xmlelement = etree.Element("airport")
        airport.render(xmlelement, airport)
        xml = etree.tostring(xmlelement, pretty_print=True)
        expected_xml = """<airport>
  <type>IATA</type>
  <code>WAW</code>
</airport>
"""
        self.assertEqual(expected_xml, xml)

    def test_attribute_rendering(self):
        aircraft = Aircraft()
        aircraft.tail_number = "LN-KKX"
        xmlelement = etree.Element("aircraft")
        aircraft.render(xmlelement, aircraft)
        expected_xml = """<aircraft tail_number="LN-KKX"/>\n"""
        xml = etree.tostring(xmlelement, pretty_print=True)
        self.assertEqual(expected_xml, xml)

    def test_attribute_parsing(self):
        XML = """<aircraft tail_number="LN-KKX"/>\n"""
        aircraft = Aircraft.parsexml(XML)
        self.assertEqual("LN-KKX", aircraft.tail_number)

    def test_mulitylayer_complex(self):
        flight = Flight()
        flight.tail_number = "LN-KKA"
        flight.takeoff_airport = Airport.create("IATA", "WAW")
        flight.landing_airport = Airport.create("ICAO", "EGLL")

        try:
            flight.takeoff_pilot = "ABC"
        except ValueError:
            pass
        else:
            self.assertTrue(False)  # Should't get here.
        flight.takeoff_pilot = "CAPTAIN"

        xmlelement = etree.Element("flight")
        flight.render(xmlelement, flight)
        xml = etree.tostring(xmlelement, pretty_print=True)
        expected_xml = """<flight>
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
"""
        self.assertEqual(expected_xml, xml)

    def test_complex_with_list(self):
        flight = Flight()
        flight.tail_number = "LN-KKA"
        flight.takeoff_airport = Airport.create("IATA", "WAW")
        flight.landing_airport = Airport.create("ICAO", "EGLL")
        flight.passangers.append("abc")
        flight.passangers.append("123")

        xmlelement = etree.Element("flight")
        flight.render(xmlelement, flight)
        xml = etree.tostring(xmlelement, pretty_print=True)
        expected_xml = """<flight>
  <tail_number>LN-KKA</tail_number>
  <takeoff_airport>
    <type>IATA</type>
    <code>WAW</code>
  </takeoff_airport>
  <landing_airport>
    <type>ICAO</type>
    <code>EGLL</code>
  </landing_airport>
  <passanger>abc</passanger>
  <passanger>123</passanger>
</flight>
"""
        self.assertEqual(expected_xml, xml)

    def test_inheritance_rendering(self):

        class A(xsd.ComplexType):
            name = xsd.Attribute(xsd.String)

        class B(A):
            type = xsd.Attribute(xsd.String)

        b = B()
        b.name = "b"
        b.type = "B"
        xml = b.xml("inheritance")
        EXPECTED_XML = """<inheritance name="b" type="B"/>\n"""
        self.assertEqual(EXPECTED_XML, xml)

    def test_inheritance_parsin(self):

        class A(xsd.ComplexType):
            name = xsd.Attribute(xsd.String)

        class B(A):
            type = xsd.Element(xsd.String)

        XML = """<inheritance name="b">
  <type>B</type>
</inheritance>\n"""
        b = B.parsexml(XML)
        self.assertEqual(b.name, "b")
        self.assertEqual(b.type, "B")


class XmlParsingTest(unittest.TestCase):
    SIMPLE_XML = """<flight>
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
"""

    def test_simple_parsing(self):
        flight = Flight.parse_xmlelement(etree.fromstring(self.SIMPLE_XML))
        self.assertEqual("LN-KKA", flight.tail_number)
        self.assertEqual("WAW", flight.takeoff_airport.code)
        self.assertEqual("IATA", flight.takeoff_airport.type)
        self.assertEqual("EGLL", flight.landing_airport.code)
        self.assertEqual("ICAO", flight.landing_airport.type)
        self.assertEqual(iso8601.parse_date("2001-10-26T21:32:52z"), flight.takeoff_datetime)

    LIST_XML = """<flight>
  <landing_airport>
    <code>EGLL</code>
    <type>ICAO</type>
  </landing_airport>
  <passanger>abc</passanger>
  <passanger>123</passanger>
  <tail_number>LN-KKA</tail_number>
  <takeoff_airport>
    <code>WAW</code>
    <type>IATA</type>
  </takeoff_airport>
</flight>
"""

    def test_list_parsing(self):
        flight = Flight.parse_xmlelement(etree.fromstring(self.LIST_XML))
        self.assertEqual("LN-KKA", flight.tail_number)
        self.assertEqual("WAW", flight.takeoff_airport.code)
        self.assertEqual("IATA", flight.takeoff_airport.type)
        self.assertEqual("EGLL", flight.landing_airport.code)
        self.assertEqual("ICAO", flight.landing_airport.type)
        self.assertEqual(["abc", "123"], flight.passangers)


class XSD_Spec_Test(unittest.TestCase):
    AIRPORT_XML = """
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
    </xs:complexType>"""

    def test_complexType(self):
        airport = xsdspec.XSDComplexType.parse_xmlelement(etree.fromstring(self.AIRPORT_XML))
        self.assertEqual("airport", airport.name)
        code_type_element = airport.sequence.elements[0]
        code_element = airport.sequence.elements[1]
        self.assertEqual("code_type", code_type_element.name)
        self.assertEqual("xs:string", code_type_element.simpleType.restriction.base)
        self.assertEqual(3, len(code_type_element.simpleType.restriction.enumerations))
        self.assertEqual("ICAO", code_type_element.simpleType.restriction.enumerations[0].value)
        self.assertEqual("code", code_element.name)


SCHEMA_XML = """
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
</xs:schema>"""


class SchemaTest(unittest.TestCase):
    def test_schema_parsing(self):
        schema = xsdspec.Schema.parse_xmlelement(etree.fromstring(SCHEMA_XML))
        self.assertEqual(4, len(schema.complexTypes))
        self.assertEqual(1, len(schema.simpleTypes))
        self.assertEqual(2, len(schema.elements))

        self.assertEqual("ops", schema.elements[0].name)
        self.assertEqual("fds:ops", schema.elements[0].type)

        ops_type = schema.complexTypes[2]
        self.assertEqual("ops", ops_type.name)
        self.assertEqual("aircraft", ops_type.sequence.elements[0].name)
        self.assertEqual("xs:string", ops_type.sequence.elements[0].type)


class RequestResponseOperation(xsd.Group):
    input = xsd.Element(xsd.String, minOccurs=0)
    output = xsd.Element(xsd.String, minOccurs=0)


class Operation(xsd.ComplexType):
    name = xsd.Element(xsd.String)
    requestResponseOperation = xsd.Ref(RequestResponseOperation)


class GroupTest(unittest.TestCase):
    XML = """<operation>
  <name>TEST-Operation</name>
  <input>IN</input>
  <output>OUT</output>
</operation>\n"""

    def test_rendering(self):
        operation = Operation()
        operation.name = "TEST-Operation"
        operation.requestResponseOperation.input = "IN"
        operation.requestResponseOperation.output = "OUT"
        xml = operation.xml("operation")
        self.assertEqual(self.XML, xml)

    def test_parsing(self):
        operation = Operation.parsexml(self.XML)
        self.assertEqual(operation.name, "TEST-Operation")
        self.assertEqual(operation.requestResponseOperation.input, "IN")
        self.assertEqual(operation.requestResponseOperation.output, "OUT")

    def test_rendering_empty_group(self):
        operation = Operation()
        operation.name = "TEST-Operation"
        xml = operation.xml("operation")
        expected_xml = """<operation>
  <name>TEST-Operation</name>
</operation>\n"""
        self.assertEqual(expected_xml, xml)


#<xs:attributeGroup name="tHeaderAttributes">
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
        body.parts = "Parts"
        body.tBodyAttributes.use = "required"
        body.tBodyAttributes.namespace = "xs"
        expected_xml = """<body parts="Parts" use="required" namespace="xs"/>\n"""
        xml = body.xml("body")
        self.assertEqual(expected_xml, xml)

    def test_parsing(self):
        xml = """<body parts="Parts" use="required" namespace="xs"/>\n"""
        body = TBody.parsexml(xml)
        self.assertEqual(body.parts, "Parts")
        self.assertEqual(body.tBodyAttributes.use, "required")
        self.assertEqual(body.tBodyAttributes.namespace, "xs")
        self.assertEqual(body.tBodyAttributes.encodingStyle, None)


class AirporttDocument(xsd.Document):
    airport = xsd.Element(Airport)


class DocumentTest(unittest.TestCase):

    def test_document_rendering(self):
        document = AirporttDocument()
        document.airport = Airport(code="XXX", type="IATA")
        xml = document.render()
        expected_xml = """<airport>
  <type>IATA</type>
  <code>XXX</code>
</airport>\n"""
        self.assertEqual(xml, expected_xml)


class NillableTest(unittest.TestCase):

    def test_nilable_element_rendering(self):

        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.Integer, nillable=True)
            notnillable = xsd.Element(xsd.Integer, minOccurs=0)

        test = Test()
        test.value = xsd.NIL
        xml = test.xml("test")
        EXPECTED_XML = """<test>
  <value xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
</test>\n"""
        self.assertEqual(xml, EXPECTED_XML)
        try:
            test.notnillable = xsd.NIL
        except ValueError:
            pass
        else:
            self.assertTrue(False, "Should not get here.")

    def test_nillable_element_parsing(self):

        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.Long, nillable=True)

        xml = """<test><value xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/></test>"""
        test = Test.parsexml(xml)
        self.assertEquals(test.value, xsd.NIL)

    def test_nillable_list_rendering(self):

        class Test(xsd.ComplexType):
            values = xsd.ListElement(xsd.String, "value", nillable=True)
            notnillable = xsd.ListElement(xsd.String, "notnillable", minOccurs=0)

        test = Test()
        test.values.append("XXX")
        test.values.append(xsd.NIL)
        xml = test.xml("test")
        EXPECTED_XML = """<test>
  <value>XXX</value>
  <value xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
</test>\n"""
        self.assertEqual(xml, EXPECTED_XML)

        try:
            test.notnillable.append(xsd.NIL)
        except:
            pass
        else:
            self.assertTrue(False, "Should not get here.")

    def test_nillable_list_parsing(self):

        class Test(xsd.ComplexType):
            values = xsd.ListElement(xsd.Int, "value", nillable=True)

        XML = """<test>
                    <value>1</value>
                    <value xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
                    <value xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
                    <value>2</value>
                </test>
                """
        test = Test.parsexml(XML)
        self.assertEqual(test.values[0], 1)
        self.assertEqual(test.values[1], xsd.NIL)
        self.assertEqual(test.values[2], xsd.NIL)
        self.assertEqual(test.values[3], 2)

    def test_nillable_attribute(self):

        class Test(xsd.ComplexType):
            value = xsd.Attribute(xsd.String, nillable=True, use=xsd.Use.OPTIONAL)

        test = Test()
        self.assertEqual(test.xml("test"), "<test/>\n")
        test.value = xsd.NIL
        self.assertEqual('<test value="nil"/>\n', test.xml("test"))


class ElementTypeEvaluation(unittest.TestCase):

    def test_string_type_evalutation(self):

        class B1(xsd.ComplexType):
            a = xsd.Element("A1")

        class A1(xsd.ComplexType):
            pass

        b = B1()
        b.a = A1()


class PatternTest(unittest.TestCase):

    def test_string_pattern(self):

        class Test(xsd.ComplexType):
            value = xsd.Element(xsd.String(pattern=r"^a*$"))

        test = Test()
        test.value = "a"
        test.value = "aaa"
        try:
            test.value = "b"
        except ValueError:
            pass
        else:
            self.assertTrue(False, "Should not get here.")


if __name__ == "__main__":
    unittest.main()
