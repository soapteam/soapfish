# -*- coding: utf-8 -*-

from nose import SkipTest
from pythonic_testcase import PythonicTestCase, assert_equals, assert_raises

from soapfish.xsd_types import XSDDate


class XSDDateTest(PythonicTestCase):
    def test_can_instantiate_with_valid_dates(self):
        assert_equals(2014, XSDDate(2014, 11, 13).year)
        assert_equals(2012, XSDDate(2012, 2, 29).year)

    def test_raises_exception_when_instantiating_invalid_dates(self):
        assert_raises(ValueError, lambda: XSDDate(2014, 2, 50))
        assert_raises(ValueError, lambda: XSDDate(2014, 13, 10))
        assert_raises(ValueError, lambda: XSDDate(2011, 2, 29))

    def test_supports_very_distant_dates(self):
        raise SkipTest('XSDDate can currently only represent the value range of datetime.date')
        future = XSDDate(12345, 4, 21)
        assert_equals(12345, future.year)

        past = XSDDate(-12345, 4, 21)
        assert_equals(-12345, past.year)
