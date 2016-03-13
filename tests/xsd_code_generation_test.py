from __future__ import print_function

from lxml import etree
from nose import SkipTest
from pythonic_testcase import *

from soapfish import xsd, xsdspec
from soapfish import xsd2py
from soapfish.testutil import generated_symbols


class XSDCodeGenerationTest(PythonicTestCase):
    def test_can_generate_code_for_simple_element(self):
        xml = ('<xs:schema targetNamespace="http://site.example/ws/spec" \n'
            '    xmlns:example="http://site.example/ws/spec" \n'
            '    xmlns:xs="http://www.w3.org/2001/XMLSchema" \n'
            '    elementFormDefault="qualified" attributeFormDefault="unqualified">\n'
            '    <xs:element name="simpleElement" type="xs:string"/>\n'
            '</xs:schema>')
        xml_element = etree.fromstring(xml)
        code_string = xsd2py.generate_code_from_xsd(xml_element)
        
        schema, new_symbols = generated_symbols(code_string)
        assert_not_none(schema)
        assert_length(1, new_symbols)
        
        assert_equals(['simpleElement'], list(schema.elements))
        simple_element = schema.elements['simpleElement']
        assert_isinstance(simple_element._type, xsd.String)
    
    def test_can_generate_code_with_xsd_refs_to_simple_elements(self):
        raise SkipTest('References to simple elements not yet implemented')
        xml = ('<xs:schema targetNamespace="http://site.example/ws/spec" \n'
            '    xmlns:example="http://site.example/ws/spec" \n'
            '    xmlns:xs="http://www.w3.org/2001/XMLSchema" \n'
            '    elementFormDefault="qualified">\n'
            '    <xs:element name="name" type="xs:string" />\n'
            '    <xs:element name="job">\n'
            '        <xs:complexType>\n'
            '            <xs:sequence>\n'
            '                <xs:element ref="example:name" />\n'
            '            </xs:sequence>\n'
            '        </xs:complexType>\n'
            '    </xs:element>\n'
            '</xs:schema>')
        xml_element = etree.fromstring(xml)
        code_string = xsd2py.generate_code_from_xsd(xml_element)
        
        schema, new_symbols = generated_symbols(code_string)
        assert_not_none(schema)
        # somehow we need to be able to have a schema with multiple possible
        # root elements
        assert_length(3, new_symbols)
        assert_contains('Name', new_symbols.keys())
        assert_contains('Job', new_symbols.keys())
        
        assert_equals(set(['name', 'job']), list(schema.elements))
        
        Job = new_symbols['Job']
        Name = new_symbols['Name']
        name_ref = Job.name
        # not sure if these assertions are correct but they should give you
        # the idea
        assert_isinstance(name_ref, xsd.Ref)
        assert_equals(name_ref._type, Name)
        
        job = Job()
        # Should not raise
        job.name = u'Foo'
        # probably we need to check some more stuff here
    
    def test_can_generate_code_with_xsd_refs_to_elements_with_anoynmous_complex_types(self):
        raise SkipTest('References to elements with anonymous complex types are not yet implemented')
        # The final test should have an object graph representation of the
        # schema below. Currently I don't know how to represent multiple
        # xs:elements in a schema without using ComplexTypes.
        # Maybe we should have a special type like AnonymousComplexType and
        # put that directly into schema.elements?
        xml = ('<xs:schema targetNamespace="http://site.example/ws/spec" \n'
            '    xmlns:example="http://site.example/ws/spec" \n'
            '    xmlns:xs="http://www.w3.org/2001/XMLSchema" \n'
            '    elementFormDefault="qualified">\n'
            '    <xs:element name="person">\n'
            '        <xs:complexType>\n'
            '            <xs:sequence>\n'
            '                <xs:element name="name" type="xs:string" />\n'
            '            </xs:sequence>\n'
            '        </xs:complexType>\n'
            '    </xs:element>\n'
            '    <xs:element name="job">\n'
            '        <xs:complexType>\n'
            '            <xs:sequence>\n'
            '                <xs:element ref="example:person" />\n'
            '            </xs:sequence>\n'
            '        </xs:complexType>\n'
            '    </xs:element>\n'
            '</xs:schema>')
        xml_element = etree.fromstring(xml)
        generated_schema = xsdspec.Schema.parse_xmlelement(xml_element)
        code_string = xsd2py.schema_to_py(generated_schema, ['xs'])
        
        schema, new_symbols = generated_symbols(code_string)
        assert_not_none(schema)
        assert_length(3, new_symbols)
        assert_contains('Person', new_symbols.keys())
        assert_contains('Job', new_symbols.keys())
        
        assert_equals(set(['person', 'job']), list(schema.elements))
        
        Job = new_symbols['Job']
        Person = new_symbols['Person']
        person_ref = Job.person
        assert_isinstance(person_ref, xsd.Ref)
        assert_equals(person_ref._type, Person)
        
        job = Job()
        person = Person()
        person.name = u'Foo'
        job.person = person
        # Check generated XML
        # <job><person><name>Foo</name></person></job>
    
    def test_implicit_target_namespace(self):
        xml = ('<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" \n'
            '    elementFormDefault="qualified">\n'
            '    <xs:element name="field" type="xsd:string" />\n'
            '</xs:schema>')
        xml_element = etree.fromstring(xml)
        generated_schema = xsdspec.Schema.parse_xmlelement(xml_element)
        xsd2py.schema_to_py(generated_schema, ['xs'],
                            parent_namespace="http://site.example/ws/spec")

    def test_can_generate_list_enumeration(self):
        raise SkipTest('list enumerations are not parsed correctly from xsd')
        xml = '<xsd:schema elementFormDefault="qualified" targetNamespace="http://example.org/A" xmlns:xsd="http://www.w3.org/2001/XMLSchema">' \
              '    <xsd:simpleType name="MyList">' \
              '        <xsd:list>' \
              '            <xsd:simpleType>' \
              '                <xsd:restriction base="xsd:string">' \
              '                    <xsd:enumeration value="A"/>' \
              '                    <xsd:enumeration value="B"/>' \
              '                    <xsd:enumeration value="C"/>' \
              '                </xsd:restriction>' \
              '            </xsd:simpleType>' \
              '        </xsd:list>' \
              '    </xsd:simpleType>' \
              '</xsd:schema>'
        xml_element = etree.fromstring(xml)
        code_string = xsd2py.generate_code_from_xsd(xml_element)

        schema, new_symbols = generated_symbols(code_string)
        assert_not_none(schema)
        assert_length(2, new_symbols)

        assert_true(issubclass(new_symbols['MyList'], xsd.List))

        my_list = new_symbols['MyList']()
        assert_equals(my_list.accept(['B']), True)

    def test_can_generate_extension(self):
        xml = """
        <xs:schema targetNamespace="http://example.com"
                    xmlns:xs="http://www.w3.org/2001/XMLSchema"
                    elementFormDefault="qualified"
                    attributeFormDefault="unqualified">
            <xs:complexType name="ComplexType">
                <xs:complexContent>
                    <xs:extension base="Base">
                        <xs:sequence>
                            <xs:element maxOccurs="1" minOccurs="0"
                                name="Field2" type="xs:string">
                            </xs:element>
                        </xs:sequence>
                    </xs:extension>
                </xs:complexContent>
            </xs:complexType>
            <xs:complexType name="Base">
                <xs:sequence>
                    <xs:element name="Field1" type="xs:string" />
                </xs:sequence>
            </xs:complexType>
        </xs:schema>
        """
        xml_element = etree.fromstring(xml)
        code_string = xsd2py.generate_code_from_xsd(xml_element)
        schema, new_symbols = generated_symbols(code_string)
