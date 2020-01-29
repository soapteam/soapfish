import unittest

from lxml import etree

from soapfish.soap11 import Code, get_error_response


class SOAP11Test(unittest.TestCase):
    def test_get_error_response(self):
        response = get_error_response(Code.SERVER, 'some error', actor='me')
        xml = self._xml_strip(response)
        self.assertIn(b'<faultcode>Server</faultcode>', xml)
        self.assertIn(b'<faultactor>me</faultactor>', xml)

    def _xml_strip(self, xml):
        parser = etree.XMLParser(remove_blank_text=True)
        return etree.tostring(etree.fromstring(xml, parser=parser))
