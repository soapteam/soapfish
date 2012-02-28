#from lxml import etree
#import xsd
#
#SOAPTransport = "http://schemas.xmlsoap.org/soap/http"
#
#class SOAP12:
#    ENVELOPE = "http://www.w3.org/2003/05/soap-envelope"
#    BINDING = "http://schemas.xmlsoap.org/wsdl/soap12/"
#    CONTENT_TYPE = "application/soap+xml"
#    class Code:
#        CLIENT = "Sender"
#        SERVER = "Receiver"
#
#    @staticmethod
#    def determin_soap_action(request):
#        content_types = request.META["CONTENT_TYPE"].split(";")
#        for content_type in content_types:
#            if content_type.strip(" ").startswith("action="):
#                action = content_type.split("=")[1]
#                return action.replace('"',"")
#        return None
#
#    @classmethod
#    def get_error_response(cls, code, message):
#        fault = SOAP12.Fault(Code=code, Reason=message)
#        envelope = SOAP12.Envelope()
#        envelope.Body = SOAP12.Body(Fault=fault)
#        return envelope.xml("Envelope")
#
#    class Header(xsd.ComplexType):
#        """SOAP Envelope Header."""
#        pass
#
#    class Fault(xsd.ComplexType):
#        """SOAP Envelope Fault."""
#        Code = xsd.Element(xsd.String)
#        Reason = xsd.Element(xsd.String)
#
#    class Body(xsd.ComplexType):
#        """SOAP Envelope Body."""
#        message = xsd.ClassNamedElement(xsd.ComplexType, minOccurs=0)
#        Fault = xsd.Element(SOAP12.Fault, minOccurs=0)
#
#        def content(self):
#            return etree.tostring(self._xmlelement[0], pretty_print=True)
#
#    class Envelope(xsd.ComplexType):
#        """SOAP Envelope."""
#        Header = xsd.Element(Header, nillable=True)
#        Body = xsd.Element(SOAP12.Body)
#
#        @classmethod
#        def reponse(cls, return_object):
#            envelope = SOAP12.Envelope()
#            envelope.Body = SOAP12.Body()
#            envelope.Body.message = return_object
#            return envelope.xml("Envelope")
#
#    SCHEMA = xsd.Schema(
#        targetNamespace = SOAP12.ENVELOPE,
#        elementFormDefault = xsd.ElementFormDefault.QUALIFIED,
#        complexTypes = [SOAP12.Header, SOAP12.Body, SOAP12.Envelope, SOAP12.Fault])
#
##-------------------------------------------------------------------------------
#class SOAP11:
#    ENVELOPE = "http://schemas.xmlsoap.org/soap/envelope/"
#    BINDING = "http://schemas.xmlsoap.org/wsdl/soap/"
#    CONTENT_TYPE = "text/xml"
#    class Code:
#        CLIENT = "Client"
#        SERVER = "Server"
#
#    @staticmethod
#    def determin_soap_action(request):
#        if request.META.get("HTTP_SOAPACTION"):
#            return request.META.get("HTTP_SOAPACTION").replace('"','')
#        elif request.META.get("HTTP_ACTION"):
#            return request.META.get("HTTP_ACTION").replace('"','')
#        else:
#            return None
#
#    @classmethod
#    def get_error_reponse(cls, code,message):
#        fault = SOAP11.Fault(faultcode="Client", faultstring=message,detail=message)
#        envelope = SOAP11.Envelope()
#        envelope.Body = SOAP11.Body(Fault=fault)
#        return envelope.xml("Envelope")
#
#    class Header(xsd.ComplexType):
#        """SOAP Envelope Header."""
#        pass
#
#    class Fault(xsd.ComplexType):
#        """SOAP Envelope Fault."""
#        faultcode = xsd.Element(xsd.String)
#        faultstring = xsd.Element(xsd.String)
#        detail = xsd.Element(xsd.String)
#
#    class Body(xsd.ComplexType):
#        """SOAP Envelope Body."""
#        message = xsd.ClassNamedElement(xsd.ComplexType, minOccurs=0)
#        Fault = xsd.Element(SOAP11.Fault, minOccurs=0)
#        def content(self):
#            return etree.tostring(self._xmlelement[0], pretty_print=True)
#
#    class Envelope(xsd.ComplexType):
#        """SOAP Envelope."""
#        Header = xsd.Element(Header, nillable=True)
#        Body = xsd.Element(SOAP11.Body)
#
#        @classmethod
#        def reponse(cls, return_object):
#            envelope = SOAP11.Envelope()
#            envelope.Body = SOAP11.Body()
#            envelope.Body.message = return_object
#            return envelope.xml("Envelope")
#
#    SCHEMA = xsd.Schema(
#        targetNamespace = SOAP11.ENVELOPE,
#        elementFormDefault = xsd.ElementFormDefault.QUALIFIED,
#        complexTypes = [SOAP11.Header, SOAP11.Body, SOAP11.Envelope, SOAP11.Fault])
#
#
#class SOAPVersion:
#    SOAP12 = SOAP12
#    SOAP11 = SOAP11
#
#    @classmethod
#    def get_version(cls, namespace):
#        if namespace == cls.SOAP11.ENVELOPE or namespace == cls.SOAP11.BINDING:
#            return cls.SOAP11
#        elif  namespace == cls.SOAP12.ENVELOPE or namespace == cls.SOAP12.BINDING:
#            return cls.SOAP11
#        else:
#            raise ValueError("SOAP version with namespace '%s' is not supported." % namespace)
#
#    @classmethod
#    def get_version_name(cls, namespace):
#        version = cls.get_version(namespace)
#        return version.__name__
#
#
#def get_django_dispatch(service):
#    def call_the_method(request,message,soap_action):
#        for method in service.methods:
#            if soap_action != method.soapAction:
#                continue
#
#            if isinstance(method.input,str):
#                element = service.schema.elements[method.input]
#                input_object = element._type.parsexml(message,service.schema)
#            else:
#                input_object = method.input.parsexml(message,service.schema)
#
#            return_object = method.function(request, input_object)
#            try:
#                return_object.xml(uncapitalize(return_object.__class__.__name__), service.schema)#Validation.
#            except Exception, e:
#                raise ValueError(e)
#            return return_object
#        raise ValueError("Method not found!")
#    #-------------------------------------------------------------
#    def django_dispatch(request):
#        from django.http import HttpResponse
#        import py2wsdl
#        SOAP = service.version
#
#        if request.method == "GET" and request.GET.has_key("wsdl"):
#            wsdl = py2wsdl.generate_wsdl(service)
#            return HttpResponse(wsdl,mimetype="text/xml")
#
#        try:
#            xml = request.raw_post_data
#            envelope = SOAP.Envelope.parsexml(xml)
#            message = envelope.Body.content()
#            soap_action = SOAP.determin_soap_action(request)
#            return_object = call_the_method(request, message, soap_action)
#            soap_message = SOAP.Envelope.reponse(return_object)
#            return HttpResponse(soap_message,content_type=SOAP.CONTENT_TYPE)
#        except (ValueError,etree.XMLSyntaxError) as e:
#            content = SOAP.get_error_message(SOAP.CODE.CLIENT,str(e))
#        except Exception, e:
#            content = SOAP.get_error_message(SOAP.CODE.SERVER,str(e))
#        return HttpResponse(content, content_type=SOAP.CONTENT_TYPE)
#
#
