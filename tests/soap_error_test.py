import unittest

from soapbox.soap import SOAPError
from soapbox.soap11 import Code

class SOAPErrorTest(unittest.TestCase):

    def test_can_clone_instances(self):
        error = SOAPError(u'message', Code.CLIENT, u'faultstring', faultactor=u'me')
        
        clone = error.copy()
        self.assertEqual(u'message', clone.message)
        self.assertEqual(Code.CLIENT, clone.faultcode)
        self.assertEqual(u'faultstring', clone.faultstring)
        self.assertEqual(u'me', clone.faultactor)
        
        clone.foo = u'bar'
        self.assertFalse(hasattr(error, 'foo'))

