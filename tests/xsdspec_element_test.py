
from nose import SkipTest

from soapbox import xsdspec
from soapbox.lib.pythonic_testcase import *


class XSDSpecElementTest(PythonicTestCase):
    def test_can_render_simple_element(self):
        element = xsdspec.Element()
        element.name = 'Name'
        element.type = 'xs:string'
        
        expected_xml = b'<element name="Name" type="xs:string"/>\n'
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
        expected_xml = (b'<element name="versionNumber">\n'
            b'  <simpleType>\n'
            b'    <restriction base="string">\n'
            b'      <pattern value="\d{2}\.\d{1,2}"/>\n'
            b'    </restriction>\n'
            b'  </simpleType>\n'
            b'</element>\n')
        assert_equals(expected_xml, element.xml('element'))
    
    def test_element_with_ref_attribute_rejects_forbidden_attributes(self):
        raise SkipTest('Elements with "ref" attribute currently do not restrict setting other attributes.')
        element = xsdspec.Element()
        element.ref = 'foo'
        element.minOccurs = 3
        element.maxOccurs = '6'
        # element.id (not present in xsdspec.Element)
        
        def set_(attribute, value):
            return lambda: setattr(element, attribute, value)
        assert_raises(ValueError, set_('name', u'bar'))
        assert_raises(ValueError, set_('type', u'xs:string'))
        assert_raises(ValueError, set_('nillable', u'True'))
        
        simple_type = xsdspec.SimpleType(restriction=xsdspec.Restriction(base='string'))
        assert_raises(ValueError, set_('simpleType', simple_type))
        #assert_raises(ValueError, set_('complexType', u'True'))
        
        element.ref = None
        # doesn't raise anymore because we deleted the "ref" attribute
        element.name = u'bar'

