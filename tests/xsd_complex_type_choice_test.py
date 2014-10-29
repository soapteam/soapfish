import unittest

from lxml import etree

from soapfish import xsd, xsdspec
from soapfish.lib import iso8601
from soapfish.lib.pythonic_testcase import *
from soapfish.xsd import Schema, ElementFormDefault, String, ComplexType
from soapfish.py2xsd import generate_xsd

class XSDComplexTypeChoiceTest(unittest.TestCase):
    def test_can_validate_choice_groups(self):
        class Code(xsd.String):
            pattern='[0-9]{1,3}'

        class Message(xsd.String):
            pass

        class Result(ComplexType):
            INDICATOR = xsd.Choice
            code = xsd.Element(Code)
            message = xsd.Element(Message)

        schema = Schema('http://foo.example/' ,
            elementFormDefault=ElementFormDefault.QUALIFIED,
            simpleTypes=(Code, Message),
            complexTypes=(Result, ),
            elements={'result': xsd.Element(Result)}
        )

        self.assert_is_valid(self._result_wrap('<message>foo bar</message>'), schema)
        self.assert_is_valid(self._result_wrap('<code>012</code>'), schema)
        self.assert_is_invalid(self._result_wrap('<code>123456</code>'), schema)
        self.assert_is_invalid(
            self._result_wrap('<message>foo bar</message><code>012</code>'),
            schema
        )

    def _result_wrap(self, child_string):
        return '<result xmlns="http://foo.example/">%s</result>' % child_string

    def assert_is_valid(self, xml_string, soapfish_schema):
        xml = etree.fromstring(xml_string)
        xmlschema = etree.XMLSchema(generate_xsd(soapfish_schema))
        assert_true(
            xmlschema.validate(xml),
            message="XML did not validate: %r" % xml_string
        )

    def assert_is_invalid(self, xml_string, soapfish_schema):
        xml = etree.fromstring(xml_string)
        xmlschema = etree.XMLSchema(generate_xsd(soapfish_schema))
        assert_false(
            xmlschema.validate(xml),
            message="XML should fail to validate: %r" % xml_string
        )
