from soapfish import xsd
from soapfish.testutil import SimpleTypeTestCase


class StringTest(SimpleTypeTestCase):
    def test_can_restrict_acceptable_values_with_pattern(self):
        self.xsd_type = xsd.String(pattern='1.')
        self.assert_can_set('12')
        self.assert_can_set('1a')
        self.assert_can_not_set('ab')
        self.assert_can_not_set('123')

    def test_can_restrict_acceptable_values_with_length(self):
        self.xsd_type = xsd.String(length=4)
        self.assert_can_set('1234')
        self.assert_can_not_set('12345')

    def test_can_restrict_acceptable_values_with_length_range(self):
        self.xsd_type = xsd.String(minLength=2, maxLength=4)
        self.assert_can_not_set('1')
        self.assert_can_set('12')
        self.assert_can_set('123')
        self.assert_can_set('1234')
        self.assert_can_not_set('12345')

    def test_can_check_for_restrictions_before_accepting_values(self):
        xsd_string = xsd.String(enumeration=('10', '20', '30'), pattern='1.')
        self.assertEqual('10', xsd_string.accept('10'))
        with self.assertRaises(ValueError):
            xsd_string.accept('15')
        with self.assertRaises(ValueError):
            xsd_string.accept('20')

    def test_accepts_plain_strings_even_if_subclassed(self):
        class StringWithPattern(xsd.String):
            pattern = r'[0-9]{3}'

        self.xsd_type = StringWithPattern
        stored = self.assert_can_set('123')
        self.assertEqual('123', stored)
        self.assert_can_not_set('abc')
        self.assert_can_not_set('1234')

    def test_restriction_whitespace_preserve(self):
        xsd_string = xsd.String(whiteSpace='preserve')
        expected = value = 'line  1\n \tline  2'
        value = xsd_string.accept(value)
        self.assertEqual(expected, value)

    def test_restriction_whitespace_replace(self):
        xsd_string = xsd.String(whiteSpace='replace')
        expected = value = 'line  1   line  2'
        value = xsd_string.accept(value)
        self.assertEqual(expected, value)

    def test_restriction_whitespace_collapse(self):
        xsd_string = xsd.String(whiteSpace='collapse')
        value = 'line  1\n \tline  2'
        expected = 'line 1 line 2'
        value = xsd_string.accept(value)
        self.assertEqual(expected, value)

    def test_apply_whitespace_restriction_before_validation(self):
        self.xsd_type = xsd.String(minLength=4, whiteSpace='collapse')
        self.assert_can_not_set('1\n  \t 2')
        self.assert_can_set('1\n  \t 23')
