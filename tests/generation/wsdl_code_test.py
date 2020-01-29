import os
import unittest.mock

from soapfish import utils, wsdl2py, xsd
from soapfish.testutil import generated_symbols


class WSDLCodeGenerationTest(unittest.TestCase):

    def test_can_generate_code_for_simple_wsdl_import(self):
        path = 'tests/assets/generation/import_simple.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        self.assertTrue(schemas)

    def test_can_generate_code_for_nested_wsdl_import(self):
        path = 'tests/assets/generation/import_nested.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        self.assertTrue(schemas)

    def test_can_generate_code_for_looped_wsdl_import(self):
        path = 'tests/assets/generation/import_looped.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        self.assertTrue(schemas)

    def test_can_generate_code_for_two_schemas(self):
        xml = utils.open_document('tests/assets/generation/multi_schema.wsdl')
        code = wsdl2py.generate_code_from_wsdl(xml, 'client')
        schemas, symbols = generated_symbols(code)
        self.assertTrue(schemas)
        self.assertEqual(len([s for s in symbols if s.startswith('Schema_')]), 2)
        self.assertEqual(['A'], list(schemas[0].elements))
        self.assertEqual(['B'], list(schemas[1].elements))

    @unittest.skip('Cannot generate code for wsdl with type inheritance')
    def test_can_generate_code_for_inheritance(self):
        xml = utils.open_document('tests/assets/generation/inheritance.wsdl')
        code = wsdl2py.generate_code_from_wsdl(xml, 'client')
        schemas, symbols = generated_symbols(code)
        self.assertTrue(schemas)
        self.assertEqual(len(symbols), 4)
        self.assertEqual(['B', 'A'], list(schemas[0].elements))
        self.assertIsInstance(schemas[0].elements['B']._type, xsd.String)
        self.assertIsInstance(schemas[0].elements['A']._type, schemas[0].elements['B']._type.__class__)

    def test_can_generate_remote_tree(self):
        def _mock(path):
            if path == 'http://example.org/xsd/simple_element.xsd':
                filename = 'tests/assets/generation/simple_element.xsd'
            else:
                self.fail('Unexpected remote path: %s' % path)

            with open(filename, 'rb') as f:
                return f.read()

        xml = utils.open_document('tests/assets/generation/import_remote.wsdl')
        with unittest.mock.patch('soapfish.xsd2py.open_document') as p:
            p.side_effect = _mock
            code = wsdl2py.generate_code_from_wsdl(
                xml,
                'client',
                cwd='http://example.org/code/')
            schemas, symbols = generated_symbols(code)
