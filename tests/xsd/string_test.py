# -*- coding: utf-8 -*-

from soapfish.lib.pythonic_testcase import *
from soapfish import xsd


class StringTest(PythonicTestCase):
    def test_can_check_for_restrictions_before_accepting_values(self):
        xsd_string = xsd.String(enumeration=('10', '20', '30'), pattern='1.')
        assert_equals('10', xsd_string.accept('10'))
        assert_raises(ValueError, lambda: xsd_string.accept('15'))
        assert_raises(ValueError, lambda: xsd_string.accept('20'))

