class DispatchTestMixin:
    def _soap_request(self, input_value):
        soap = self.service.version
        method = self.service.get_method('echoOperation')
        headers = soap.build_http_request_headers(method.soapAction)
        tagname = method.input
        element = self.service.find_element_by_name('echoRequest')
        echo = element._type.create(input_value)
        request_body = soap.Envelope.response(tagname, echo)
        return headers, request_body

    def _soap_response(self, response_body):
        soap = self.service.version
        method = self.service.get_method('echoOperation')
        envelope = soap.Envelope.parsexml(response_body)
        self.assertIsNone(envelope.Body.Fault)
        element = self.service.find_element_by_name(method.output)
        return envelope.Body.parse_as(element._type.__class__)
