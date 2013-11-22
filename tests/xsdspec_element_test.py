
from soapbox import xsdspec
from soapbox.lib.pythonic_testcase import *


class XSDSpecElementTest(PythonicTestCase):
    def test_can_render_simple_element(self):
        element = xsdspec.Element()
        element.name = 'Name'
        element.type = 'xs:string'
        
        expected_xml = u'<element name="Name" type="xs:string"/>\n'
        assert_equals(expected_xml, element.xml('element'))
    
    def test_can_render_elements_with_anonymous_simple_types(self):
        element = xsdspec.Element()
        element.name = 'versionNumber'
        element.simpleType = xsdspec.SimpleType(
            restriction=xsdspec.Restriction(
                base='string',
                pattern=xsdspec.Pattern(value='\d{2}\.\d{1,2}')
            )
        )
        expected_xml = unicode('<element name="versionNumber">\n'
            '  <simpleType>\n'
            '    <restriction base="string">\n'
            '      <pattern value="\d{2}\.\d{1,2}"/>\n'
            '    </restriction>\n'
            '  </simpleType>\n'
            '</element>\n')
        assert_equals(expected_xml, element.xml('element'))
