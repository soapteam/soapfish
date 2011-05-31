#SOAP Protocol implementation, dispatchers and client stub.
from lxml import etree
import xsd
import re
import py2wsdl
import httplib2
from utils import uncapitalize

class SOAPVersion:
    SOAP11 = "SOAP 1.1"
    SOAP12 = "SOAP 1.2"
    
#SOAP messages description objects.
class Header(xsd.ComplexType):
    """SOAP Envelope Header."""
    pass

class Fault(xsd.ComplexType):
    """SOAP Envelope Fault."""
    faultcode = xsd.Element(xsd.String)
    faultstring = xsd.Element(xsd.String)
    detail = xsd.Element(xsd.String)
    
class Body(xsd.ComplexType):
    """SOAP Envelope Body."""
    message = xsd.ClassNamedElement(xsd.ComplexType, minOccurs=0)
    Fault = xsd.Element(Fault, minOccurs=0)
    def content(self):
        return etree.tostring(self._xmlelement[0], pretty_print=True)

class Envelope(xsd.ComplexType):
    """SOAP Envelope."""
    Header = xsd.Element(Header, nilable=True) 
    Body = xsd.Element(Body)
    
    @classmethod
    def reponse(cls, return_object):
        envelope = Envelope()
        envelope.Body = Body()
        envelope.Body.message = return_object 
        return envelope.xml("Envelope")
    
Schema = xsd.Schema(
    targetNamespace = "http://schemas.xmlsoap.org/soap/envelope/",
    elementFormDefault = xsd.ElementFormDefault.QUALIFIED,
    complexTypes = [Header, Body, Envelope])

class SOAPError(Exception):
    pass
    
class Service(object):
    """Describes service aggregating informations required for dispatching 
    and WSDL generation. """ 
    def __init__(self, targetNamespace, location, schema, methods, 
                 version=SOAPVersion.SOAP11):
        """:param targetNamespace: string
           :param location: string, endpoint url.
           :param schema: xsd.Schema instance.
           :param methods: list of xsd.Methods"""
        self.targetNamespace = targetNamespace
        self.location = location
        self.schema = schema
        self.methods = methods
        self.version = version
        
    def get_method(self, operationName):
        return filter(lambda m:m.operationName ==operationName, self.methods)[0]
            

#TODO:
#1. Fault code could use Client.Authentication notation to indicate error type.
  
def get_django_dispatch(service):
    """Returns dispatch method for specified service. Dispatch method can be 
    pointed by urls.py, it will capture incoming SOAP message, translate it into 
    object and call appropriate method. Expecting return object that can be 
    translated to valid SOAP response for this service. 
        On any excpetion raised from method the response will be SOAP Fault message.
    ValueError are translated into fault code Client, other to Server.  
        Incoming and outgoing XMLs are validated against XSD generated from service 
    schema. Incorrect or missing values will cause Fault response. 
    """ 
    def get_soap_action(request):
        """Finds soapAction information in HTTP header. First tries SOAP 1.1
           soapAction and action header key, then looks into content type
           for SOAP 1.2 action key. SOAP action is important for establishing 
           which method is called in document style calls where method name
           is not wrapping the message content."""
        if request.META.get("HTTP_SOAPACTION"):
            return request.META.get("HTTP_SOAPACTION").replace('"','')
        elif request.META.get("HTTP_ACTION"):
            return request.META.get("HTTP_ACTION").replace('"','')
        else:
            content_types = request.META["CONTENT_TYPE"].split(";")
            for content_type in content_types:
                if content_type.strip(" ").startswith("action="):
                    return content_type.split("=")[1]
            return None
        
    def build_soap_message(o):
        try:
            o.xml(uncapitalize(o.__class__.__name__), service.schema)#Validation.
        except Exception, e:
            raise ValueError(e)
            
        return Envelope.reponse(o)
         
    def django_dispatch(request):
        "Dispatch method tied to service."
        #We don't want to import this in main  context as the project may be 
        #using different way of dispatching. Django would be unnessesery 
        #dependecy which is sensible to assume to be true in Django dispatch only.
        from django.http import HttpResponse
        if request.method == "GET" and request.GET.has_key("wsdl"):
            wsdl = py2wsdl.generate_wsdl(service)
            return HttpResponse(wsdl,mimetype="text/xml")
            
        try:
            xml = request.raw_post_data
            envelope = Envelope.parsexml(xml)
            message = envelope.Body.content()
            soap_action = get_soap_action(request)
          
            for method in service.methods:
                if soap_action != method.soapAction:
                    continue
                
                if isinstance(method.input,str): 
                    element = service.schema.elements[method.input]
                    input_object = element._type.parsexml(message,service.schema)
                else:
                    input_object = method.input.parsexml(message,service.schema)
                    
                return_object = method.function(request, input_object)
                soap_message = build_soap_message(return_object)
                return HttpResponse(soap_message,content_type="application/soap+xml")
            
            raise ValueError("Method not found!")
        except (ValueError,etree.XMLSyntaxError) as e:
            fault = Fault(faultcode="Client", faultstring=str(e), detail=str(e))
        except Exception, e:
            #Presents of detail element indicates that the problem is related 
            #to procesing Body element. See 4.4 SOAP Fault on
            #http://www.w3.org/TR/2000/NOTE-SOAP-20000508/ 
            fault = Fault(faultcode="Server", faultstring=str(e), detail=str(e))
        envelope = Envelope()
        envelope.Body = Body(Fault=fault)
        return HttpResponse(envelope.xml("Envelope"), content_type="application/soap+xml")        
    return django_dispatch


class Stub(object):
    """Client stub. Handles only document style calls.""" 
    SERVICE = None
    
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
    
    def _build_header(self, method):
        if self.SERVICE.version == SOAPVersion.SOAP11:
            return {"content-type" : 'text/xml',
                     "SOAPAction"   : method.soapAction}
        elif self.SERVICE.version == SOAPVersion.SOAP12:
            return {"content-type" : "application/soap+xml;action=%s" % method.soapAction}
        else:
            raise ValueError("SOAP Version not supported %s" % self.SERVICE.version)
        
    def _handle_response(self, method, response, content):
        envelope = Envelope.parsexml(content)
        if envelope.Body.Fault:
            raise SOAPError("Fault Code:%s, Fault String: %s" % 
                               (envelope.Body.Fault.faultcode,
                                envelope.Body.Fault.faultstring))
        message = envelope.Body.content()
        
        if isinstance(method.output, str):
            element = self.SERVICE.schema.elements[method.output]
            _type = element._type
        else:
            _type = method.output
            
        if self.SERVICE.schema:
            return _type.parsexml(message, self.SERVICE.schema)
        else:
            return _type.parsexml(message)
        
        
    def call(self, operationName, parameter):
        #Will raise: lxml.etree.XMLSyntaxError on validation problems.
        parameter.xml(parameter.__class__.__name__.lower(), self.SERVICE.schema)
            
        h = httplib2.Http()
        if self.username:
            h.add_credentials(self.username, self.password)
        
        method = self.SERVICE.get_method(operationName)    
        headers = self._build_header(method)    
        envelope = Envelope.reponse(parameter)
    
        response, content = h.request(self.SERVICE.location, "POST",
             body=envelope, headers=headers)
        return self._handle_response(method, response, content)
        
        
        

        
                    
            
        
        
    