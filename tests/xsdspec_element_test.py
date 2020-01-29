import unittest

from soapfish import xsd, xsdspec


class XSDSpecElementTest(unittest.TestCase):
    def test_can_render_simple_element(self):
        element = xsdspec.Element()
        element.name = 'Name'
        element.type = 'xs:string'

        expected_xml = b'<element name="Name" type="xs:string"/>\n'
        self.assertEqual(expected_xml, element.xml('element'))

    def test_can_render_elements_with_anonymous_simple_types(self):
        element = xsdspec.Element()
        element.name = 'versionNumber'
        element.simpleType = xsdspec.SimpleType(
            restriction=xsdspec.Restriction(
                base='string',
                pattern=xsdspec.Pattern(value=r'\d{2}\.\d{1,2}'),
            ),
        )
        expected_xml = (
            b'<element name="versionNumber">\n'
            b'  <simpleType>\n'
            b'    <restriction base="string">\n'
            b'      <pattern value="\\d{2}\\.\\d{1,2}"/>\n'
            b'    </restriction>\n'
            b'  </simpleType>\n'
            b'</element>\n'
        )
        self.assertEqual(expected_xml, element.xml('element'))

    @unittest.skip('Elements with "ref" attribute currently do not restrict setting other attributes.')
    def test_element_with_ref_attribute_rejects_forbidden_attributes(self):
        element = xsdspec.Element()
        element.ref = 'foo'
        element.minOccurs = 3
        element.maxOccurs = '6'
        # element.id (not present in xsdspec.Element)

        def set_(attribute, value):
            return lambda: setattr(element, attribute, value)
        with self.assertRaises(ValueError):
            set_('name', 'bar')
        with self.assertRaises(ValueError):
            set_('type', 'xs:string')
        with self.assertRaises(ValueError):
            set_('nillable', 'True')

        simple_type = xsdspec.SimpleType(restriction=xsdspec.Restriction(base='string'))
        with self.assertRaises(ValueError):
            set_('simpleType', simple_type)
        # with self.assertRaises(ValueError):
        #     set_('complexType', 'True')

        element.ref = None
        # doesn't raise anymore because we deleted the "ref" attribute
        element.name = 'bar'

    def test_can_get_set_max_occurs_with_simple_value(self):
        xsd_element = xsdspec.Element()
        xsd_element.maxOccurs = 1
        self.assertEqual(1, xsd_element.maxOccurs)

    def test_can_get_set_max_occurs_with_unbounded(self):
        xsd_element = xsdspec.Element()
        xsd_element.maxOccurs = xsd.UNBOUNDED
        self.assertEqual(xsd.UNBOUNDED, xsd_element.maxOccurs)
