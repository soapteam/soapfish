
from __future__ import absolute_import

from datetime import timedelta as TimeDelta

from soapbox.lib.pythonic_testcase import *
from soapbox.utils import timezone_offset_to_string


class FormatOffsetTest(PythonicTestCase):
    def test_can_format_positive_offsets(self):
        assert_equals('+00:00', timezone_offset_to_string(TimeDelta(0)))
        assert_equals('+04:27', timezone_offset_to_string(TimeDelta(hours=4, minutes=27)))
        assert_equals('+14:00', timezone_offset_to_string(TimeDelta(hours=14)))

    def test_can_format_negative_offsets(self):
        assert_equals('-00:30', timezone_offset_to_string(TimeDelta(minutes=-30)))
        assert_equals('-01:30', timezone_offset_to_string(TimeDelta(minutes=-90)))
        assert_equals('-14:00', timezone_offset_to_string(TimeDelta(hours=-14)))

