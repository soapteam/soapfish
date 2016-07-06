
from __future__ import absolute_import, unicode_literals

from lxml import etree
from pythonic_testcase import PythonicTestCase, assert_false, assert_true

from soapfish import xsd
from soapfish.py2xsd import generate_xsd


class py2xsdTest(PythonicTestCase):
    def test_can_generate_schema_xml_containing_types_with_pattern_restriction(self):
        ns = 'http://soap.example/pattern.xsd'

        class Container(xsd.ComplexType):
            code = xsd.Element(xsd.String(pattern='[0-9]{0,5}'))
        schema = xsd.Schema(ns,
                            location=ns,
                            elementFormDefault=xsd.ElementFormDefault.QUALIFIED,
                            complexTypes=(
                                Container,
                            ),
                            elements={
                                'foo': xsd.Element(Container),
                            },
                            )
        # previously this would fail
        xsd_element = generate_xsd(schema)
        xmlschema = etree.XMLSchema(xsd_element)
        valid_xml = '<foo xmlns="%s"><code>1234</code></foo>' % ns

        def is_valid(s):
            return xmlschema.validate(etree.fromstring(s))
        assert_true(is_valid(valid_xml))

        bad_xml = '<foo xmlns="%s"><code>abc</code></foo>' % ns
        assert_false(is_valid(bad_xml))
