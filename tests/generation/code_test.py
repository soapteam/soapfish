import os
import tempfile
import textwrap
import unittest

import six
from lxml import etree
from pythonic_testcase import *  # noqa

from soapfish import py2wsdl, utils, wsdl2py, xsd2py


class CodeGenerationTest(unittest.TestCase):

    def _exec(self, code, globalz):
        _, fn = tempfile.mkstemp(suffix='.py')
        header = textwrap.dedent('''\
            # -*- coding: utf-8 -*-
            import sys
            sys.path.append('{0}')
        ''').format(os.path.dirname(fn)).encode('utf8')
        code = header + b'\n' + code + b'\n'
        with open(fn, 'wb') as f:
            # Empty last line is mandatory for python2.6
            f.write(code)
        compile(code, fn, 'exec')
        globalz['__name__'] = fn.rsplit('/', 1)[-1].rsplit('.', 1)[0]
        exec(code, globalz)

    def _check_reparse_wsdl(self, base, target):
        xml = py2wsdl.tostring(base['PutOpsPort_SERVICE'])
        code = wsdl2py.generate_code_from_wsdl(xml, target)
        m = {}
        self._exec(code, m)
        # XXX too much autonaming magic
        m['PutOpsPort_SERVICE'] = m.pop('PutOpsPortPort_SERVICE')
        if target == 'client':
            m['PutOpsPortServiceStub'] = m.pop('PutOpsPortPortServiceStub')
        assert_equals(sorted(m), sorted(base))

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
        code = wsdl2py.generate_code_from_wsdl(xml, 'server', cwd=os.path.dirname(path))
        if six.PY3:
            code = code.decode()
        assert_contains('Schema2_Element', code)
        assert_contains('Schema3_Element', code)
        assert_equals(1, code.count('Schema3_Element'))

    def test_import_same_namespace(self):
        path = 'tests/assets/same_namespace/same_namespace.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'server', cwd=os.path.dirname(path))
        if six.PY3:
            code = code.decode()
        assert_contains('Schema1_Element', code)
        assert_contains('Schema2_Element', code)

    def test_schema_xsd_include(self):
        path = 'tests/assets/include/include.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'server', cwd=os.path.dirname(path))
        if six.PY3:
            code = code.decode()
        assert_contains('Schema1_Element', code)

    def test_schema_xsd_restriction(self):
        xml = utils.open_document('tests/assets/generation/restriction.xsd')
        code = xsd2py.generate_code_from_xsd(xml)
        if six.PY3:
            code = code.decode()
        assert_contains('RestrictedString', code)

    def test_create_method_list_param(self):
        xml = utils.open_document('tests/assets/generation/list_param.xsd')
        code = xsd2py.generate_code_from_xsd(xml)
        if six.PY3:
            code = code.decode()
        assert_contains('def create(cls, Items):', code)
        assert_contains('instance.Items = Items', code)
        assert_not_contains('Itemss', code)
