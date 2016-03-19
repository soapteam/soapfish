import os
import unittest

from pythonic_testcase import *  # noqa

from soapfish import utils, wsdl2py, xsd
from soapfish.testutil import generated_symbols


class WSDLCodeGenerationTest(PythonicTestCase):

    def test_can_generate_code_for_simple_wsdl_import(self):
        path = 'tests/assets/generation/import_simple.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    def test_can_generate_code_for_nested_wsdl_import(self):
        path = 'tests/assets/generation/import_nested.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    def test_can_generate_code_for_looped_wsdl_import(self):
        path = 'tests/assets/generation/import_looped.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    def test_can_generate_code_for_two_schemas(self):
        xml = utils.open_document('tests/assets/generation/multi_schema.wsdl')
        code = wsdl2py.generate_code_from_wsdl(xml, 'client')
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)
        assert_length(4, symbols)
        assert_equals(['A'], list(schemas[0].elements))
        assert_equals(['B'], list(schemas[1].elements))

    @unittest.skip('Cannot generate code for wsdl with type inheritance')
    def test_can_generate_code_for_inheritance(self):
        xml = utils.open_document('tests/assets/generation/inheritance.wsdl')
        code = wsdl2py.generate_code_from_wsdl(xml, 'client')
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)
        assert_length(4, symbols)
        assert_equals(['B', 'A'], list(schemas[0].elements))
        assert_isinstance(schemas[0].elements['B']._type, xsd.String)
        assert_isinstance(schemas[0].elements['A']._type, schemas[0].elements['B']._type.__class__)
