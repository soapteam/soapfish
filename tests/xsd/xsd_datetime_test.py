import unittest
from datetime import datetime, timedelta, timezone, tzinfo

from lxml import etree

from soapfish import xsd


class DatetimeTest(unittest.TestCase):

    def test_rendering(self):
        dt = datetime(2001, 10, 26, 21, 32, 52)
        mixed = xsd.Element(xsd.DateTime)
        xmlelement = etree.Element('flight')
        mixed.render(xmlelement, 'takeoff_datetime', dt)
        expected_xml = b'''<flight>
  <takeoff_datetime>2001-10-26T21:32:52</takeoff_datetime>
</flight>
'''
        xml = etree.tostring(xmlelement, pretty_print=True)
        self.assertEqual(expected_xml, xml)

    def test_rendering_timezones(self):
        fake_tz = timezone(timedelta(hours=1, minutes=15))
        dt = datetime(2001, 10, 26, 21, 32, 52, tzinfo=fake_tz)
        rendered_xml = xsd.DateTime().xmlvalue(dt)
        self.assertEqual('2001-10-26T21:32:52+01:15', rendered_xml)

    def test_wrong_type(self):
        mixed = xsd.Element(xsd.DateTime)
        xmlelement = etree.Element('flight')
        self.assertRaises(Exception, lambda: mixed.render(xmlelement, 'takeoff_datetime', 1))

    def test_parsing_utctimezone(self):
        class Test(xsd.ComplexType):
            datetime = xsd.Element(xsd.DateTime)
        XML = '<root><datetime>2011-06-30T00:19:00+0000</datetime></root>'
        test = Test.parsexml(XML)
        self.assertEqual(datetime(2011, 6, 30, 0, 19, 0), test.datetime.replace(tzinfo=None))

    def test_parsing_timezone(self):
        class Test(xsd.ComplexType):
            datetime = xsd.Element(xsd.DateTime)
        XML = '<root><datetime>2011-06-30T20:19:00+01:00</datetime></root>'
        test = Test.parsexml(XML)
        self.assertEqual(datetime(2011, 6, 30, 19, 19, 0, tzinfo=timezone.utc), test.datetime.astimezone(timezone.utc))

    def test_can_correctly_determine_utc_offset(self):
        # Ensure that the DateTime type really uses the correct UTC offset depending on the passed datetime value.
        class SummerWinterTZ(tzinfo):
            def utcoffset(self, dt):
                return timedelta(0) if dt.month in (10, 11, 12, 1, 2, 3) else timedelta(hours=1)

            def dst(self, dt):
                return timedelta(hours=1)

        tz = SummerWinterTZ()
        xsd_dt = xsd.DateTime()
        self.assertEqual('2013-11-26T00:00:00+00:00', xsd_dt.xmlvalue(datetime(2013, 11, 26, tzinfo=tz)))
        self.assertEqual('2013-07-26T00:00:00+01:00', xsd_dt.xmlvalue(datetime(2013, 7, 26, tzinfo=tz)))
