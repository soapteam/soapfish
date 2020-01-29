import unittest

from soapfish import xsd


class SchemaTest(unittest.TestCase):
    def test_can_lookup_element_by_name(self):
        class CodeType(xsd.String):
            pattern = r'[0-9]{5}'

        ns = 'http://soap.example/schema.xsd'
        schema = xsd.Schema(
            ns,
            location=ns,
            elementFormDefault=xsd.ElementFormDefault.QUALIFIED,
            simpleTypes=[CodeType],
            elements={'code': xsd.Element(CodeType)},
        )
        schema_element = schema.get_element_by_name('code')
        self.assertEqual(CodeType, schema_element._passed_type)
        self.assertIsNone(schema.get_element_by_name('invalid'))
