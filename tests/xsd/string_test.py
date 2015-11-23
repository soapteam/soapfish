# -*- coding: utf-8 -*-

from pythonic_testcase import *

from soapfish import xsd
from soapfish.testutil import SimpleTypeTestCase


class StringTest(SimpleTypeTestCase):
    def test_can_restrict_acceptable_values_with_pattern(self):
        self.xsd_type = xsd.String(pattern='1.')
        self.assert_can_set('12')
        self.assert_can_set('1a')
        self.assert_can_not_set('ab')
        self.assert_can_not_set('123')

    def test_can_check_for_restrictions_before_accepting_values(self):
        xsd_string = xsd.String(enumeration=('10', '20', '30'), pattern='1.')
        assert_equals('10', xsd_string.accept('10'))
        assert_raises(ValueError, lambda: xsd_string.accept('15'))
        assert_raises(ValueError, lambda: xsd_string.accept('20'))

    def test_accepts_plain_strings_even_if_subclassed(self):
        class StringWithPattern(xsd.String):
            pattern = r'[0-9]{3}'
        self.xsd_type = StringWithPattern
        stored = self.assert_can_set('123')
        assert_equals('123', stored)
        self.assert_can_not_set('abc')
        self.assert_can_not_set('1234')
