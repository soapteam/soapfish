from __future__ import print_function

from nose import SkipTest
from pythonic_testcase import PythonicTestCase, assert_length, assert_equals, assert_not_none, assert_isinstance

from soapfish import xsd
from soapfish import wsdl2py
from soapfish.testutil import generated_symbols


class XSDCodeGenerationTest(PythonicTestCase):
    def test_can_generate_code_for_two_schemas(self):
        raise SkipTest('can not generate code for wsdl with multiple schemas')
        xml = '<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:b="http://example.org/B">'\
              '    <wsdl:types>'\
              '        <xsd:schema elementFormDefault="qualified" targetNamespace="http://example.org/A">' \
              '            <xsd:import namespace="http://example.org/B"/>' \
              '            <xsd:element name="A" type="b:B"/>' \
              '        </xsd:schema>' \
              '        <xsd:schema elementFormDefault="qualified" targetNamespace="http://example.org/B">'\
              '            <xsd:element name="B" type="xsd:string"/>'\
              '        </xsd:schema>'\
              '    </wsdl:types>'\
              '</wsdl:definitions>'
        code_string = wsdl2py.generate_code_from_wsdl(xml, 'client')

        schema, new_symbols = generated_symbols(code_string)
        assert_not_none(schema)
        assert_length(4, new_symbols)

        assert_equals(['B', 'A'], list(schema.elements))

    def test_can_generate_code_for_inheritance(self):
        raise SkipTest('can not generate code for wsdl with type inheritance')
        xml = '<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns:xsd="http://www.w3.org/2001/XMLSchema">' \
              '    <wsdl:types>' \
              '        <xsd:schema elementFormDefault="qualified" targetNamespace="http://example.org/A">' \
              '            <xsd:element name="A" type="B"/>' \
              '            <xsd:element name="B" type="xsd:string"/>' \
              '        </xsd:schema>' \
              '    </wsdl:types>' \
              '</wsdl:definitions>'
        code_string = wsdl2py.generate_code_from_wsdl(xml, 'client')

        schema, new_symbols = generated_symbols(code_string)
        assert_not_none(schema)
        assert_length(4, new_symbols)

        assert_equals(['B', 'A'], list(schema.elements))
        assert_isinstance(schema.elements['B']._type, xsd.String)
        assert_isinstance(schema.elements['A']._type, schema.elements['B']._type.__class__)
