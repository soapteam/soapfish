import unittest

from pythonic_testcase import *  # noqa

from soapfish import utils, wsdl2py, xsd
from soapfish.testutil import generated_symbols


class WSDLCodeGenerationTest(PythonicTestCase):

    @unittest.skip('Cannot generate code for wsdl with multiple schemas')
    def test_can_generate_code_for_two_schemas(self):
        xml = utils.open_document('tests/assets/generation/multi_schema.wsdl')
        code = wsdl2py.generate_code_from_wsdl(xml, 'client')

        schema, new_symbols = generated_symbols(code)
        assert_not_none(schema)
        assert_length(4, new_symbols)

        assert_equals(['B', 'A'], list(schema.elements))

    @unittest.skip('Cannot generate code for wsdl with type inheritance')
    def test_can_generate_code_for_inheritance(self):
        xml = utils.open_document('tests/assets/generation/inheritance.wsdl')
        code = wsdl2py.generate_code_from_wsdl(xml, 'client')

        schema, new_symbols = generated_symbols(code)
        assert_not_none(schema)
        assert_length(4, new_symbols)

        assert_equals(['B', 'A'], list(schema.elements))
        assert_isinstance(schema.elements['B']._type, xsd.String)
        assert_isinstance(schema.elements['A']._type, schema.elements['B']._type.__class__)
