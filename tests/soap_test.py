import unittest
from soapbox import soap, soap11, soap12

SOAP11_ERROR_MESSAGE = """
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
   <SOAP-ENV:Body>
      <SOAP-ENV:Fault>
         <faultcode>Result</faultcode>
         <faultstring/>
         <faultactor>Resultset empty2.</faultactor>
         <detail/>
      </SOAP-ENV:Fault>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
"""

SOAP11_ERROR_MESSAGE_NO_ACTOR = """
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
   <SOAP-ENV:Body>
      <SOAP-ENV:Fault>
         <faultcode>Result</faultcode>
         <faultstring>String</faultstring>
         <detail/>
      </SOAP-ENV:Fault>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
"""

SOAP12_ERROR_ROLE = """<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope">
<env:Header/><env:Body>
<env:Fault>
<env:Code><env:Value>env:Sender</env:Value></env:Code>
<env:Reason><env:Text xml:lang="en-US">
Message does not have necessary info
</env:Text></env:Reason>
<env:Role>http://gizmos.com/order</env:Role>
<env:Detail>
<PO:order xmlns:PO="http://gizmos.com/orders/">
Quantity element does not have a value</PO:order>
<PO:confirmation xmlns:PO="http://gizmos.com/confirm">
Incomplete address: no zip code</PO:confirmation>
</env:Detail></env:Fault>
</env:Body></env:Envelope>
"""

SOAP12_ERROR_NOROLE = """<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope">
<env:Header/><env:Body>
<env:Fault>
<env:Code><env:Value>env:Sender</env:Value></env:Code>
<env:Reason><env:Text xml:lang="en-US">
Message does not have necessary info
</env:Text></env:Reason>
<env:Detail>
<PO:order xmlns:PO="http://gizmos.com/orders/">
Quantity element does not have a value</PO:order>
<PO:confirmation xmlns:PO="http://gizmos.com/confirm">
Incomplete address: no zip code</PO:confirmation>
</env:Detail></env:Fault>
</env:Body></env:Envelope>
"""

class ErrorHandling(unittest.TestCase):
    def test_soap11_actor_parsing(self):
        envelope = soap11.Envelope.parsexml(SOAP11_ERROR_MESSAGE)
        code, message, actor = soap11.parse_fault_message(envelope.Body.Fault)
        self.assertEqual(code, "Result")
        self.assertEqual(message, None)
        self.assertEqual(actor, "Resultset empty2.")
        
    def test_soap11_noactor_parsing(self):
        envelope = soap11.Envelope.parsexml(SOAP11_ERROR_MESSAGE_NO_ACTOR)
        code, message, actor = soap11.parse_fault_message(envelope.Body.Fault)
        self.assertEqual(code, "Result")
        self.assertEqual(message, "String")
        self.assertEqual(actor, None)
        
    def test_soap11_fault_handling(self):
        stub = soap.Stub(location="empty")
        stub.SERVICE = soap.Service(
            name=None,
            targetNamespace=None,
            location="mock_location",
            schema=None,
            version=soap.SOAPVersion.SOAP11,
            methods=[])
        
        try:
            stub._handle_response(None, None, SOAP11_ERROR_MESSAGE)
        except soap.SOAPError,e:
              self.assertEqual(e.faultcode, "Result")
              self.assertEqual(e.faultstring, None)
              self.assertEqual(e.faultactor, "Resultset empty2.")
        else:
            self.assertFalse("true", "should not get here")
        
    def test_soap12_actor_parsing(self):
        envelope = soap12.Envelope.parsexml(SOAP12_ERROR_ROLE)
        code, message, actor = soap12.parse_fault_message(envelope.Body.Fault)
        self.assertEqual(code,"env:Sender")
        self.assertEqual(message, "\nMessage does not have necessary info\n")
        self.assertEqual(actor, "http://gizmos.com/order")
        
    def test_soap12_noactor_parsing(self):
        envelope = soap12.Envelope.parsexml(SOAP12_ERROR_NOROLE)
        code, message, actor = soap12.parse_fault_message(envelope.Body.Fault)
        self.assertEqual(code,"env:Sender")
        self.assertEqual(message, "\nMessage does not have necessary info\n")
        self.assertEqual(actor, None)
        
    def test_soap12_fault_handling(self):
        stub = soap.Stub(location="empty")
        stub.SERVICE = soap.Service(
            name=None,
            targetNamespace=None,
            location="mock_location",
            schema=None,
            version=soap.SOAPVersion.SOAP12,
            methods=[])
        
        try:
            stub._handle_response(None, None, SOAP12_ERROR_ROLE)
        except soap.SOAPError,e:
             self.assertEqual(e.faultcode,"env:Sender")
             self.assertEqual(e.faultstring, "\nMessage does not have necessary info\n")
             self.assertEqual(e.faultactor, "http://gizmos.com/order")
        else:
            self.assertFalse("true", "should not get here")
        
        
        
   
        
if __name__ == "__main__":
    unittest.main()