"""
Code Generation Tests using the W3C WSDL 2.0 Test Suite as samples.
"""
import os
import unittest

from pythonic_testcase import (
    PythonicTestCase,
    assert_is_not_empty,
)

from soapfish import utils, wsdl2py
from soapfish.testutil import generated_symbols


class ClientCodeGenerationTest(PythonicTestCase):

    # noinspection PyMethodMayBeStatic
    # TODO: Implement the functionality to pass this test.
    @unittest.expectedFailure
    def test_binding_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Binding-1B/BadBinding.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_binding_2b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Binding-2B/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_binding_3b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Binding-3B/NonUniqueBinding-Extended.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # TODO: Implement the functionality to pass this test.
    @unittest.expectedFailure
    def test_binding_4b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Binding-4B/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_binding_5b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Binding-5B/Binding.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_binding_6b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Binding-6B/Binding.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_binding_7b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Binding-7B/Binding.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_binding_fault_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/BindingFault-1B/BindingFault.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_binding_fault_reference_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/BindingFaultReference-1B/BindingFaultReference.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_binding_fault_reference_2b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/BindingFaultReference-2B/BindingFaultReference.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_binding_fault_reference_3b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/BindingFaultReference-3B/BindingFaultReference.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_binding_message_reference_1b(self):
        path = \
            'tests/assets/test_suites/w3c_wsdl20/documents/bad/BindingMessageReference-1B/BindingMessageReference.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_binding_message_reference_2b(self):
        path = \
            'tests/assets/test_suites/w3c_wsdl20/documents/bad/BindingMessageReference-2B/BindingMessageReference.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_binding_message_reference_3b(self):
        path = \
            'tests/assets/test_suites/w3c_wsdl20/documents/bad/BindingMessageReference-3B/BindingMessageReference.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_binding_operation_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/BindingOperation-1B/BindingOperation.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_chameleon_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Chameleon-1B/getBalance.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_chameleon_2b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Chameleon-2B/getBalance.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_chat_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Chat-1B/Chat-NoBindingInterface.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_chat_2b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Chat-2B/Chat-MissBindOperation.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_description_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Description-1B/Description.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_description_2b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Description-2B/Description.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_echo_2b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Echo-2B/echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_http_binding_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/HTTPBinding-1B/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_http_binding_2b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/HTTPBinding-2B/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_http_binding_3b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/HTTPBinding-3B/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_http_binding_4b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/HTTPBinding-4B/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_http_binding_5b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/HTTPBinding-5B/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_http_binding_6b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/HTTPBinding-6B/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_http_binding_7b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/HTTPBinding-7B/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_http_binding_8b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/HTTPBinding-8B/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_import_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Import-1B/XSDImport.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_import_2b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Import-2B/XSDImportInWSDL.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_import_3b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Import-3B/XSDImport2.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_import_4b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Import-4B/EchoImpl.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_import_5b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Import-5B/EchoImpl.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_import_6b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Import-6B/EchoImpl.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_import_7b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Import-7B/EchoImpl.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_import_8b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Import-8B/EchoImpl.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_include_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Include-1B/EchoImpl.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_include_2b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Include-2B/EchoImpl.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Interface-1B/Interface.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_2b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Interface-2B/Interface.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_3b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Interface-3B/Interface.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_4b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Interface-4B/Interface.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_5b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Interface-5B/Interface2.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_6b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Interface-6B/reservation.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_fault_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/InterfaceFault-1B/InterfaceFault.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_fault_2b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/InterfaceFault-2B/InterfaceFault.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_fault_3b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/InterfaceFault-3B/InterfaceFault.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_fault_reference_1b(self):
        path = \
            'tests/assets/test_suites/w3c_wsdl20/documents/bad/InterfaceFaultReference-1B/InterfaceFaultReference.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_fault_reference_2b(self):
        path = \
            'tests/assets/test_suites/w3c_wsdl20/documents/bad/InterfaceFaultReference-2B/InterfaceFaultReference.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_message_reference_1b(self):
        path = 'tests/assets/test_suites/' + \
               'w3c_wsdl20/documents/bad/InterfaceMessageReference-1B/InterfaceMessageReference.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_message_reference_2b(self):
        path = 'tests/assets/test_suites/' + \
               'w3c_wsdl20/documents/bad/InterfaceMessageReference-2B/InterfaceMessageReference.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_message_reference_3b(self):
        path = 'tests/assets/test_suites/' + \
               'w3c_wsdl20/documents/bad/InterfaceMessageReference-3B/InterfaceMessageReference.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_message_reference_4b(self):
        path = 'tests/assets/test_suites/' + \
               'w3c_wsdl20/documents/bad/InterfaceMessageReference-4B/InterfaceMessageReference.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # TODO: This test is likely incorrect. Seems to require operating on BOTH wsdl files as input, not just one.
    @unittest.skip('Multi File Test Case, Currently unsupported')
    def test_interface_operation_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/InterfaceOperation-1B/echo-extended.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_operation_3b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/InterfaceOperation-3B/InterfaceOperation.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_operation_4b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/InterfaceOperation-4B/InterfaceOperation.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_operation_5b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/InterfaceOperation-5B/InterfaceOperation.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_operation_6b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/InterfaceOperation-6B/InterfaceOperation.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_1b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/IRI-1B/iristyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_2b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/IRI-2B/iristyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_3b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/IRI-3B/iristyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_4b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/IRI-4B/iristyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_5b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/IRI-5B/iristyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_6b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/IRI-6B/iristyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_7b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/IRI-7B/iristyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_8b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/IRI-8B/iristyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_9b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/IRI-9B/iristyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_10b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/IRI-10B/iristyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_11b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/IRI-11B/iristyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_12b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/IRI-12B/iristyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_13b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/IRI-13B/iristyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_14b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/IRI-14B/iristyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_15b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/IRI-15B/iristyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_16b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/IRI-16B/iristyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_location_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Location-1B/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_location_2b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Location-2B/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_location_3b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Location-3B/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_location_4b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Location-4B/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_location_5b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Location-5B/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_location_6b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Location-6B/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_location_7b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Location-7B/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_multipart_1b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Multipart-1B/multipartstyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_multipart_2b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Multipart-2B/multipartstyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_multipart_3b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Multipart-3B/multipartstyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_multipart_4b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Multipart-4B/multipartstyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_multipart_5b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Multipart-5B/multipartstyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_multipart_6b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Multipart-6B/multipartstyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_multipart_7b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Multipart-7B/multipartstyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_multipart_8b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Multipart-8B/multipartstyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_multipart_9b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Multipart-9B/multipartstyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_multipart_10b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Multipart-10B/multipartstyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_1b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-1B/rpcstyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_2b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-2B/rpcstyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_3b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-3B/rpcstyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_4b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-4B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_5b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-5B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_6b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-6B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_7b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-7B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_8b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-8B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_9b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-9B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_10b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-10B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_11b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-11B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_12b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-12B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_13b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-13B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_14b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-14B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_15b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-15B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_16b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-16B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_17b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-17B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_18b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-18/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_19b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-19B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_20b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-20B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_21b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-21B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_22b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-22B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_23b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-23B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_24b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-24B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_25b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-25B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_26b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-26B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_27b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-27B/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_28b(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/RPC-28B/rpcstyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_schema_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Schema-1B/Schema.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_schema_2b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Schema-2B/Schema.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_schema_3b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Schema-3B/Schema.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_schema_4b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Schema-4B/Schema.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_schema_5b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Schema-5B/Schema.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_schema_6b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Schema-6B/Schema.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_schema_7b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Schema-7B/Schema.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_service_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Service-1B/Service.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_service_2b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Service-2B/Service.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_service_3b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Service-3B/Service-extended.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_service_4b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Service-4B/Service.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_service_12b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Service-12B/Service.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_service_13b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Service-13B/Service.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_service_14b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Service-14B/Service.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_service_15b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/Service-15B/Service.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_ticket_agent_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/TicketAgent-1B/TicketAgent-bad.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_unknown_extension_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/UnknownExtension-1B/Interface.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def test_wsdlx_1b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/wsdlx-1B/wsdlx.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def test_wsdlx_2b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/wsdlx-2B/wsdlx.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def test_wsdlx_3b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/wsdlx-3B/wsdlx.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def test_wsdlx_4b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/wsdlx-4B/wsdlx.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def test_wsdlx_5b(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/bad/wsdlx-5B/wsdlx.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

