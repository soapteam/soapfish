import unittest

from soapfish.xsd_types import XSDDate


class XSDDateTest(unittest.TestCase):
    def test_can_instantiate_with_valid_dates(self):
        self.assertEqual(2014, XSDDate(2014, 11, 13).year)
        self.assertEqual(2012, XSDDate(2012, 2, 29).year)

    def test_raises_exception_when_instantiating_invalid_dates(self):
        with self.assertRaises(ValueError):
            XSDDate(2014, 2, 50)
        with self.assertRaises(ValueError):
            XSDDate(2014, 13, 10)
        with self.assertRaises(ValueError):
            XSDDate(2011, 2, 29)

    @unittest.skip('XSDDate can currently only represent the value range of datetime.date')
    def test_supports_very_distant_dates(self):
        future = XSDDate(12345, 4, 21)
        self.assertEqual(12345, future.year)

        past = XSDDate(-12345, 4, 21)
        self.assertEqual(-12345, past.year)
