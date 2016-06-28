# -*- coding: utf-8 -*-

from pythonic_testcase import PythonicTestCase, assert_equals, assert_none

from soapfish import xsd


class SchemaTest(PythonicTestCase):
    def test_can_lookup_element_by_name(self):
        ns = 'http://soap.example/schema.xsd'

        class CodeType(xsd.String):
            pattern = r'[0-9]{5}'
        schema = xsd.Schema(ns,
                            location=ns,
                            elementFormDefault=xsd.ElementFormDefault.QUALIFIED,
                            simpleTypes=[CodeType],
                            elements={'code': xsd.Element(CodeType)}
                            )
        schema_element = schema.get_element_by_name('code')
        assert_equals(CodeType, schema_element._passed_type)

        assert_none(schema.get_element_by_name('invalid'))
