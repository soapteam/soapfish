
from __future__ import absolute_import

from lxml import etree
from pythonic_testcase import *

from soapfish.soap12 import Code, get_error_response


class SOAP12Test(PythonicTestCase):
    def test_get_error_response(self):
        response = get_error_response(Code.SERVER, u'some error', actor='me')
        xml = self._xml_strip(response)
        assert_contains(b'<ns0:Code><ns0:Value>ns0:Receiver</ns0:Value></ns0:Code>', xml)
        assert_contains(b'<ns0:Role>me</ns0:Role>', xml)

    def _xml_strip(self, xml):
        parser = etree.XMLParser(remove_blank_text=True)
        return etree.tostring(etree.fromstring(xml, parser=parser))
