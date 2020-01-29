import unittest
from datetime import timedelta

from soapfish.utils import timezone_offset_to_string


class FormatOffsetTest(unittest.TestCase):
    def test_can_format_positive_offsets(self):
        self.assertEqual('+00:00', timezone_offset_to_string(timedelta(0)))
        self.assertEqual('+04:27', timezone_offset_to_string(timedelta(hours=4, minutes=27)))
        self.assertEqual('+14:00', timezone_offset_to_string(timedelta(hours=14)))

    def test_can_format_negative_offsets(self):
        self.assertEqual('-00:30', timezone_offset_to_string(timedelta(minutes=-30)))
        self.assertEqual('-01:30', timezone_offset_to_string(timedelta(minutes=-90)))
        self.assertEqual('-14:00', timezone_offset_to_string(timedelta(hours=-14)))
