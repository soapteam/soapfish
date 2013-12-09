
from __future__ import absolute_import

from lxml import etree

from soapbox.lib.pythonic_testcase import *
from soapbox.soap11 import get_error_response, Code


class SOAP11Test(PythonicTestCase):
    def test_get_error_response(self):
        response = get_error_response(Code.SERVER, u'some error', actor='me')
        xml = self._xml_strip(response)
        assert_contains('<faultcode>Server</faultcode>', xml)
        assert_contains('<faultactor>me</faultactor>', xml)
    
    def _xml_strip(self, xml):
        parser = etree.XMLParser(remove_blank_text=True)
        return etree.tostring(etree.fromstring(xml, parser=parser))
