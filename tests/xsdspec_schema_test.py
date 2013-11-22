
from soapbox import xsdspec
from soapbox.lib.pythonic_testcase import *


class XSDSpecSchemaTest(PythonicTestCase):
    def test_can_parse_references(self):
        xml = unicode('<xs:schema targetNamespace="http://site.example/ws/spec" \n'
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
        schema = xsdspec.Schema.parsexml(xml)
        
        job_element = schema.elements[1]
        assert_equals('job', job_element.name)
        
        person_reference = job_element.complexType.sequence.elements[0]
        assert_none(person_reference.name)
        assert_equals('example:person', person_reference.ref)
        
        person_element = schema.elements[0]
        assert_equals('person', person_element.name)
        # TODO: check that the person_reference points to person

