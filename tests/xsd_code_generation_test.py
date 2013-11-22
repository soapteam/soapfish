
from lxml import etree

from soapbox import xsd
from soapbox import xsd2py
from soapbox.lib.pythonic_testcase import *


class XSDCodeGenerationTest(PythonicTestCase):
    def test_can_generate_code_for_simple_element(self):
        xml = unicode('<xs:schema targetNamespace="http://site.example/ws/spec" \n'
            '    xmlns:example="http://site.example/ws/spec" \n'
            '    xmlns:xs="http://www.w3.org/2001/XMLSchema" \n'
            '    elementFormDefault="qualified" attributeFormDefault="unqualified">\n'
            '    <xs:element name="simpleElement" type="xs:string"/>\n'
            '</xs:schema>')
        xml_element = etree.fromstring(xml)
        code_string = xsd2py.generate_code_from_xsd(xml_element)
        
        schema, new_symbols = self._generated_symbols(code_string)
        assert_not_none(schema)
        assert_length(1, new_symbols)
        
        assert_equals(['simpleElement'], list(schema.elements))
        simple_element = schema.elements['simpleElement']
        assert_isinstance(simple_element._type, xsd.String)
    
    def _generated_symbols(self, code_string):
        # imports not present in generated code
        from soapbox import xsd
        from soapbox.xsd import UNBOUNDED
        locals_ = set(locals())
        locals_.add('locals_')
        
        try:
            # Let's trust our own code generation...
            exec code_string
        except Exception:
            print code_string
            raise
        new_locals = locals()
        new_variables = set(new_locals).difference(locals_)
        
        schema = None
        new_symbols = dict()
        for name in new_variables:
            symbol_ = new_locals[name]
            new_symbols[name] = symbol_
            if isinstance(symbol_, xsd.Schema):
                schema = symbol_
        return schema, new_symbols

