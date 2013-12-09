
from __future__ import absolute_import

from lxml import etree

from soapbox.lib.pythonic_testcase import *
from soapbox.soap12 import get_error_response, Code


class SOAP11Test(PythonicTestCase):
    def test_get_error_response(self):
        response = get_error_response(Code.SERVER, u'some error')
        xml = self._xml_strip(response)
        assert_contains('<ns0:Code><ns0:Value>ns0:Receiver</ns0:Value></ns0:Code>', xml)
    
    def _xml_strip(self, xml):
        parser = etree.XMLParser(remove_blank_text=True)
        return etree.tostring(etree.fromstring(xml, parser=parser))
