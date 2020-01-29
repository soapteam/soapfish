import os
import tempfile
import textwrap
import unittest

from lxml import etree

from soapfish import py2wsdl, utils, wsdl2py, xsd2py


class CodeGenerationTest(unittest.TestCase):

    def _exec(self, code, globalz):
        _, fn = tempfile.mkstemp(suffix='.py')
        header = textwrap.dedent('''\
            import sys
            sys.path.append(r'{0}')
        ''').format(os.path.dirname(fn).rstrip('\\')).encode()
        code = header + b'\n' + code + b'\n'
        with open(fn, 'wb') as f:
            f.write(code)
        compile(code, fn, 'exec')
        globalz['__name__'] = os.path.basename(fn).rsplit('.', 1)[0]
        exec(code, globalz)

    def _check_reparse_wsdl(self, base, target):
        tree = py2wsdl.generate_wsdl(base['PutOpsPort_SERVICE'])
        xml = etree.tostring(tree, pretty_print=True)
        code = wsdl2py.generate_code_from_wsdl(xml, target)
        m = {}
        self._exec(code, m)
        # XXX too much autonaming magic
        m['PutOpsPort_SERVICE'] = m.pop('PutOpsPortPort_SERVICE')
        if target == 'client':
            m['PutOpsPortServiceStub'] = m.pop('PutOpsPortPortServiceStub')
        self.assertEqual(sorted(m), sorted(base))

    def test_code_generation_from_xsd(self):
        xml = utils.open_document('tests/assets/generation/default.xsd')
        # Add mandatory imports to test the generated code
        code = xsd2py.generate_code_from_xsd(xml)
        self._exec(code, {})

    def test_code_generation_from_wsdl_client(self):
        xml = utils.open_document('tests/assets/generation/default.wsdl')
        code = wsdl2py.generate_code_from_wsdl(xml, 'client')
        m = {}
        self._exec(code, m)
        self._check_reparse_wsdl(m, 'client')

    def test_code_generation_from_wsdl_server(self):
        xml = utils.open_document('tests/assets/generation/default.wsdl')
        code = wsdl2py.generate_code_from_wsdl(xml, 'server')
        m = {}
        self._exec(code, m)
        self._check_reparse_wsdl(m, 'server')

    def test_relative_paths(self):
        path = 'tests/assets/relative/relative.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'server', cwd=os.path.dirname(path)).decode()
        self.assertIn('Schema2_Element', code)
        self.assertIn('Schema3_Element', code)
        self.assertEqual(1, code.count('Schema3_Element'))

    def test_import_same_namespace(self):
        path = 'tests/assets/same_namespace/same_namespace.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'server', cwd=os.path.dirname(path)).decode()
        self.assertIn('Schema1_Element', code)
        self.assertIn('Schema2_Element', code)

    def test_schema_xsd_include(self):
        path = 'tests/assets/include/include.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'server', cwd=os.path.dirname(path)).decode()
        self.assertIn('Schema1_Element', code)

    def test_schema_xsd_enumeration(self):
        xml = utils.open_document('tests/assets/generation/enumeration2.xsd')
        code = xsd2py.generate_code_from_xsd(xml)
        m = {}
        try:
            self._exec(code, m)
        except SyntaxError as e:
            self.fail('%s: %s' % (e.__class__.__name__, e))

    def test_schema_xsd_restriction(self):
        xml = utils.open_document('tests/assets/generation/restriction.xsd')
        code = xsd2py.generate_code_from_xsd(xml).decode()
        self.assertIn('RestrictedString', code)
        self.assertIn("pattern=r'[a-z]+'", code)

    def test_create_method_list_param(self):
        xml = utils.open_document('tests/assets/generation/list_param.xsd')
        code = xsd2py.generate_code_from_xsd(xml).decode()
        self.assertIn('def create(cls, Items):', code)
        self.assertIn('instance.Items = Items', code)
        self.assertNotIn('Itemss', code)
