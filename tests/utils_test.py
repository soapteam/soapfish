from __future__ import absolute_import

from datetime import timedelta

from pythonic_testcase import PythonicTestCase, assert_equals

from soapfish.utils import timezone_offset_to_string


class FormatOffsetTest(PythonicTestCase):
    def test_can_format_positive_offsets(self):
        assert_equals('+00:00', timezone_offset_to_string(timedelta(0)))
        assert_equals('+04:27', timezone_offset_to_string(timedelta(hours=4, minutes=27)))
        assert_equals('+14:00', timezone_offset_to_string(timedelta(hours=14)))

    def test_can_format_negative_offsets(self):
        assert_equals('-00:30', timezone_offset_to_string(timedelta(minutes=-30)))
        assert_equals('-01:30', timezone_offset_to_string(timedelta(minutes=-90)))
        assert_equals('-14:00', timezone_offset_to_string(timedelta(hours=-14)))
