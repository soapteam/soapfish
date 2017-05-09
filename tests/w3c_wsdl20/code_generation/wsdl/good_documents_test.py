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
    def test_chameleon_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Chameleon-1G/getBalance.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_chameleon_2g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Chameleon-2G/getBalance.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_chameleon_3g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Chameleon-3G/getBalance.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_chameleon_4g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Chameleon-4G/getBalance.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_compound_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Compound1-1G/compound1.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_credit_card_faults_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/CreditCardFaults-1G/use-credit-card-faults.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # TODO: Implement the functionality to pass this test.
    @unittest.expectedFailure
    def test_echo_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Echo-1G/echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_echo_2g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Echo-2G/echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_echo_complex_doc_lit_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/EchoComplexDocLit-1G/Axis2SampleDocLit.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def test_flickr_http_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/FlickrHTTP-1G/flickr.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_great_h_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/GreatH-1G/primer-hotelReservationService.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_great_h_2g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/GreatH-2G/primer-hotelReservationService.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_great_h_3g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/GreatH-3G/primer-hotelReservationService.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_http_binding_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/HTTPBinding-1G/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_http_binding_2g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/HTTPBinding-2G/Echo.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_import_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Import-1G/XSDImport.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_import_2g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Import-2G/XSDImport2.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_imported_wsdl_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/ImportedWSDL-1G/updateDetails.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_include_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Include-1G/EchoImpl.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_in_only_mep_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/InOnlyMEP-1G/Oneway.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Interface-1G/Interface.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_2g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Interface-2G/Interface.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_3g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Interface-3G/Interface.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_4g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Interface-4G/Interface.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_5g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Interface-5G/Interface.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_6g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Interface-6G/Interface.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_interface_7g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Interface-7G/Interface.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_1g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/IRI-1G/iristyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_2g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/IRI-2G/iristyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_iri_3g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/IRI-3G/iristyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_location_template_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/LocationTemplate-1G/SOAPService.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_location_template_2g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/LocationTemplate-2G/SOAPService.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_location_template_3g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/LocationTemplate-3G/SOAPService.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_message_multipart_1g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/MessageMultipart-1G/HTTPservice.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_message_test_1g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/MessageTest-1G/SOAPservice.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_message_test_2g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/MessageTest-2G/HTTPservice.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_message_test_3g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/MessageTest-3G/HTTPservice.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_message_test_4g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/MessageTest-4G/SOAPservice.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_message_test_5g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/MessageTest-5G/SOAPservice.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_message_test_6g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/MessageTest-6G/SOAPservice.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_module_composition_1g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/ModuleComposition-1G/SOAPservice.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_multipart_1g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Multipart-1G/multipartstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_multipart_2g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Multipart-2G/multipartstyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_multipart_3g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Multipart-3G/multipartstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_multiple_inline_schemas_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/MultipleInlineSchemas-1G/retrieveItems.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_1g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/RPC-1G/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_2g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/RPC-2G/rpcstyleinonly.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_3g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/RPC-3G/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_4g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/RPC-4G/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_5g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/RPC-5G/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_rpc_6g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/RPC-6G/rpcstyleinout.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def test_sawsdl_0g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/SAWSDL-0G/00-plain.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    # TODO: This test requires both files be processed in order to properly perform the test.
    @unittest.skip('Multi File Test Case, Currently unsupported')
    def test_sawsdl_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/SAWSDL-1G/01-multiple-inheritance-annotation.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def test_sawsdl_3g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/SAWSDL-3G/03-operation-annotation.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def test_sawsdl_4g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/SAWSDL-4G/04-fault-annotation.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    # TODO: This test requires both files be processed in order to properly perform the test.
    @unittest.skip('Multi File Test Case, Currently unsupported')
    def test_sawsdl_5g(self):
        path = 'tests/assets/' \
               'test_suites/w3c_wsdl20/documents/good/SAWSDL-5G/05-simpletype-annotation-with-attribute.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    # TODO: This test requires both files be processed in order to properly perform the test.
    @unittest.skip('Multi File Test Case, Currently unsupported')
    def test_sawsdl_6g(self):
        path = 'tests/assets/' \
               'test_suites/w3c_wsdl20/documents/good/SAWSDL-6G/06-multiple-complextype-annotation.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def test_sawsdl_7g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/SAWSDL-7G/07-element-annotation.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def test_sawsdl_8g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/SAWSDL-8G/08-attribute-annotation.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    @unittest.skip('Multi File Test Case, Currently unsupported')
    # TODO: This test requires both files be processed in order to properly perform the test.
    def test_sawsdl_9g(self):
        path = 'tests/assets/' \
               'test_suites/w3c_wsdl20/documents/good/SAWSDL-9G/09-multiple-element-lifting.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def test_sawsdl_10g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/SAWSDL-10G/10-type-lifting.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def test_sawsdl_11g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/SAWSDL-11G/11-element-lowering.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    @unittest.skip('Multi File Test Case, Currently unsupported')
    # TODO: This test requires both files be processed in order to properly perform the test.
    def test_sawsdl_12g(self):
        path = 'tests/assets/' \
               'test_suites/w3c_wsdl20/documents/good/SAWSDL-12G/12-type-lowering.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    @unittest.skip('Multi File Test Case, Currently unsupported')
    # TODO: This test requires both files be processed in order to properly perform the test.
    def test_sawsdl_13g(self):
        path = 'tests/assets/' \
               'test_suites/w3c_wsdl20/documents/good/SAWSDL-13G/13-mapping-propagation.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def test_sawsdl_14g(self):
        path = 'tests/assets/' \
               'test_suites/w3c_wsdl20/documents/good/SAWSDL-14G/05-simpletype-annotation-with-attribute.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_schema_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Schema-1G/string.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_schema_id_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/SchemaId-1G/schemaIds.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_schema_location_fragment_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/SchemaLocationFragment-1G/Items.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_service_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Service-1G/Service.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_service_2g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Service-2G/Service.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_service_3g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Service-3G/Service.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # TODO: This test requires both files be processed in order to properly perform the test.
    @unittest.skip('Multi File Test Case, Currently unsupported')
    def test_service_reference_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/ServiceReference-1G/reservationList.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_soap_header_1g(self):
        # noinspection SpellCheckingInspection
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/SOAPHeader-1G/SOAPservice.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def test_sparql_query_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/SparqlQuery-1G/sparql-protocol-query.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def test_sparql_query_simplified_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/SparqlQuerySimplified-1G/sparql-protocol-query.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_storage_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Storage-1G/storage.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_storage_2g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Storage-2G/storage.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_storage_3g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Storage-3G/storage.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_storage_4g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Storage-4G/storage.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_storage_5g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/Storage-5G/storage.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_ticket_agent_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/TicketAgent-1G/TicketAgent.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_unknown_extension_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/UnknownExtension-1G/Interface.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_unknown_extension_2g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/UnknownExtension-2G/Interface.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def test_w3c_bugzilla_http_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/W3CBugzillaHttp-1G/w3c-bugzilla.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_wealth_svc_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/WealthSvc-1G/WealthSvc.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_ws_addressing_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/WSAddressing-1G/wsaTestService2.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_xs_import_1g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/XsImport-1G/reservation.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_xs_import_2g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/XsImport-2G/reservationDetails.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

    # noinspection PyMethodMayBeStatic
    def test_xs_import_3g(self):
        path = 'tests/assets/test_suites/w3c_wsdl20/documents/good/XsImport-3G/reservationDetails.wsdl'
        xml = utils.open_document(path)
        code = wsdl2py.generate_code_from_wsdl(xml, 'client', cwd=os.path.dirname(path))
        schemas, symbols = generated_symbols(code)
        assert_is_not_empty(schemas)

