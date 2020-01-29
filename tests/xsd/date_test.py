from datetime import date, datetime, timedelta, timezone, tzinfo

from lxml import etree

from soapfish import xsd
from soapfish.testutil import SimpleTypeTestCase
from soapfish.xsd_types import XSDDate


class DateTest(SimpleTypeTestCase):
    xsd_type = xsd.Date

    def test_can_render_python_date(self):
        date_ = date(2001, 10, 26)
        xmlelement = etree.Element('foo')
        xsd.Element(self.xsd_type).render(xmlelement, 'bar', date_)
        xml = self._normalize(etree.tostring(xmlelement, pretty_print=True))
        self.assertEqual(b'<foo><bar>2001-10-26</bar></foo>', xml)

    def test_rendering_timezones(self):
        date_ = XSDDate(2001, 10, 26, tzinfo=timezone(timedelta(hours=1, minutes=15)))
        rendered_xml = self.xsd_type().xmlvalue(date_)
        self.assertEqual('2001-10-26+01:15', rendered_xml)

    def test_wrong_type(self):
        mixed = xsd.Element(xsd.DateTime)
        xmlelement = etree.Element('foo')
        with self.assertRaises(Exception):
            mixed.render(xmlelement, 'bar', 1)

    def test_parsing_utctimezone(self):
        class Test(xsd.ComplexType):
            datetime_ = xsd.Element(xsd.DateTime, tagname='datetime')
        parsed = Test.parsexml('<root><datetime>2011-06-30T00:19:00+0000</datetime></root>')
        self.assertEqual(datetime(2011, 6, 30, 0, 19, 0, tzinfo=timezone.utc), parsed.datetime_)

    def test_parsing_timezone(self):
        class Test(xsd.ComplexType):
            datetime_ = xsd.Element(xsd.DateTime, tagname='datetime')
        parsed = Test.parsexml('<root><datetime>2011-06-30T20:19:00+01:00</datetime></root>')
        self.assertEqual(datetime(2011, 6, 30, 20, 19, 0, tzinfo=timezone(timedelta(hours=1))), parsed.datetime_)

    def test_can_correctly_determine_utc_offset(self):
        # Ensure that the DateTime type really uses the correct UTC offset
        # depending on the passed datetime value.
        class SummerWinterTZ(tzinfo):
            def utcoffset(self, dt):
                if dt.month in (10, 11, 12, 1, 2, 3):
                    return timedelta(0)
                return timedelta(hours=1)

            def dst(self, dt):
                return timedelta(hours=1)
        tz = SummerWinterTZ()
        xsd_dt = xsd.DateTime()
        self.assertEqual('2013-11-26T00:00:00+00:00', xsd_dt.xmlvalue(datetime(2013, 11, 26, tzinfo=tz)))
        self.assertEqual('2013-07-26T00:00:00+01:00', xsd_dt.xmlvalue(datetime(2013, 7, 26, tzinfo=tz)))

    def test_accepts_only_compatible_types(self):
        self.assert_can_set(None)
        self.assert_can_set(XSDDate(2012, 10, 26))
        self.assert_can_set(date(2013, 10, 26))

        self.assert_can_not_set(0)
        self.assert_can_not_set([])
        self.assert_can_not_set('invalid')
        self.assert_can_not_set(datetime(2013, 10, 26))

    def test_parsing(self):
        self.assert_parse(None, None)
        self.assert_parse(None, 'nil')
        self.assert_parse(XSDDate(2012, 10, 26), '2012-10-26')
        self.assert_parse(XSDDate(2016, 2, 29, tzinfo=timezone.utc), '2016-02-29Z')
        parsed_date = self._parse('2012-02-29+01:00')
        self.assertEqual(date(2012, 2, 29), parsed_date.as_datetime_date())
        self.assertEqual(timezone(timedelta(hours=1)).utcoffset(None), parsed_date.tzinfo.utcoffset(None))

        parsed_date = self._parse('2012-02-29-02:30')
        self.assertEqual(date(2012, 2, 29), parsed_date.as_datetime_date())
        self.assertEqual(timezone(-timedelta(hours=2, minutes=30)).utcoffset(None), parsed_date.tzinfo.utcoffset(None))
