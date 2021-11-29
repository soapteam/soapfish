import unittest

from soapfish.core import SOAPResponse


class SOAPResponseHandling(unittest.TestCase):
    def test_constructor(self):
        response = SOAPResponse('', http_status_code=500)
        self.assertEqual(500, response.http_status_code)
