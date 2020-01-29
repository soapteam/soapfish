from soapfish import xsd
from soapfish.testutil import SimpleTypeTestCase


class DecimalTest(SimpleTypeTestCase):
    def test_can_restrict_acceptable_values_with_pattern(self):
        self.xsd_type = xsd.Decimal(pattern='1.')
        self.assert_can_set(12)
        self.assert_can_not_set(123)
