import unittest

from lxml import etree

from soapfish import xsd
from soapfish.py2xsd import generate_xsd
from soapfish.xsd import ComplexType, ElementFormDefault, Schema


class XSDChoiceTest(unittest.TestCase):
    def _choice_schema(self):
        class Code(xsd.String):
            pattern = '[0-9]{1,3}'

        class Message(xsd.String):
            pass

        class Result(ComplexType):
            INDICATOR = xsd.Choice
            code = xsd.Element(Code)
            message = xsd.Element(Message)

        return Schema(
            'http://foo.example/',
            elementFormDefault=ElementFormDefault.QUALIFIED,
            simpleTypes=(Code, Message),
            complexTypes=(Result, ),
            elements={'result': xsd.Element(Result)},
        )

    def test_can_validate_choice_groups(self):
        schema = self._choice_schema()
        self.assert_is_valid(self._result_wrap('<message>foo bar</message>'), schema)
        self.assert_is_valid(self._result_wrap('<code>012</code>'), schema)
        self.assert_is_invalid(self._result_wrap('<code>123456</code>'), schema)
        self.assert_is_invalid(self._result_wrap('<message>foo bar</message><code>012</code>'), schema)

    def test_can_parse_choice_groups(self):
        schema = self._choice_schema()
        Result = schema.elements['result']._type

        xml = '<message>foo bar</message>'
        self.assert_is_valid(self._result_wrap(xml), schema)
        result = Result.parse_xmlelement(etree.fromstring(xml))
        self.assertEqual('foo bar', result.message)
        self.assertIsNone(result.code)

        xml = '<code>123</code>'
        self.assert_is_valid(self._result_wrap(xml), schema)
        result = Result.parse_xmlelement(etree.fromstring(xml))
        self.assertIsNone(result.message)
        self.assertEqual('123', result.code)

    def _result_wrap(self, child_string):
        return '<result xmlns="http://foo.example/">%s</result>' % child_string

    def assert_is_valid(self, xml_string, soapfish_schema):
        xml = etree.fromstring(xml_string)
        xmlschema = etree.XMLSchema(generate_xsd(soapfish_schema))
        self.assertIs(xmlschema.validate(xml), True, msg='XML did not validate: %r' % xml_string)

    def assert_is_invalid(self, xml_string, soapfish_schema):
        xml = etree.fromstring(xml_string)
        xmlschema = etree.XMLSchema(generate_xsd(soapfish_schema))
        self.assertIs(xmlschema.validate(xml), False, msg='XML should fail to validate: %r' % xml_string)
