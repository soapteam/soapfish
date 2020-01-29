import unittest

from lxml import etree

from .. import xsd

__all__ = ['SimpleTypeTestCase']


class SimpleTypeTestCase(unittest.TestCase):
    xsd_type = None

    # --- custom assertions ---------------------------------------------------
    def assert_parse(self, expected_value, string_value):
        self.assertEqual(expected_value, self._parse(string_value))

    def assert_can_set(self, value):
        class Container(xsd.ComplexType):
            foo = xsd.Element(self.xsd_type)
        container = Container()
        container.foo = value
        return container.foo

    def assert_can_not_set(self, value):
        class Container(xsd.ComplexType):
            foo = xsd.Element(self.xsd_type)
        container = Container()
        try:
            container.foo = value
        except ValueError:
            pass
        else:
            self.fail('did accept forbidden value %r' % value)

    # --- internal helpers ----------------------------------------------------
    def _parse(self, string_value):
        class Container(xsd.ComplexType):
            foo = xsd.Element(self.xsd_type)
        if string_value is None:
            string_value = ''
        xml = '<container><foo>%s</foo></container>' % string_value
        return Container.parsexml(xml).foo

    def _normalize(self, xml):
        parser = etree.XMLParser(remove_blank_text=True)
        return etree.tostring(etree.XML(xml, parser=parser))
