import unittest
from datetime import datetime

from lxml import etree

from soapbox import xsd
from soapbox import iso8601


class DatetimeTest(unittest.TestCase):

    def test_rendering(self):
        dt = datetime(2001, 10, 26, 21, 32, 52)
        mixed = xsd.Element(xsd.DateTime)
        xmlelement = etree.Element("flight")
        mixed.render(xmlelement, "takeoff_datetime", dt)
        expected_xml = """<flight>
  <takeoff_datetime>2001-10-26T21:32:52</takeoff_datetime>
</flight>
"""
        xml = etree.tostring(xmlelement, pretty_print=True)
        self.assertEqual(expected_xml, xml)

    def test_rendering_timezones(self):
        fake_tz = iso8601.FixedOffset(1, 15, 'dummy zone')
        dt = datetime(2001, 10, 26, 21, 32, 52, tzinfo=fake_tz)
        rendered_xml = xsd.DateTime().xmlvalue(dt)
        self.assertEqual('2001-10-26T21:32:52+01:15', rendered_xml)

    def test_wrong_type(self):
        mixed = xsd.Element(xsd.DateTime)
        xmlelement = etree.Element("flight")
        self.assertRaises(Exception, lambda: mixed.render(xmlelement, "takeoff_datetime", 1))

    def test_parsing_utctimezone(self):
        class Test(xsd.ComplexType):
            datetime = xsd.Element(xsd.DateTime)
        XML = """<root><datetime>2011-06-30T00:19:00+0000Z</datetime></root>"""
        test = Test.parsexml(XML)
        self.assertEqual(datetime(2011, 6, 30, 0, 19, 0), test.datetime.replace(tzinfo=None))

    def test_parsing_timezone(self):
        class Test(xsd.ComplexType):
            datetime = xsd.Element(xsd.DateTime)
        XML = """<root><datetime>2011-06-30T20:19:00+01:00</datetime></root>"""
        test = Test.parsexml(XML)
        self.assertEqual(datetime(2011, 6, 30, 19, 19, 0), test.datetime.astimezone(iso8601.UTC).replace(tzinfo=None))

