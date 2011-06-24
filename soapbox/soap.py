#SOAP Protocol implementation, dispatchers and client stub.
from lxml import etree
import xsd
import httplib2
import soap11
import soap12
from utils import uncapitalize

SOAP_HTTP_Transport = "http://schemas.xmlsoap.org/soap/http"
                    
class SOAPVersion:
    SOAP12 = soap12
    SOAP11 = soap11
    
    @classmethod
    def get_version(cls, namespace):
        if namespace == cls.SOAP11.ENVELOPE or namespace == cls.SOAP11.BINDING:
            return cls.SOAP11
        elif  namespace == cls.SOAP12.ENVELOPE or namespace == cls.SOAP12.BINDING:
            return cls.SOAP11
        else:
            raise ValueError("SOAP version with namespace '%s' is not supported." % namespace)
        
    @classmethod
    def get_version_name(cls, namespace):
        version = cls.get_version(namespace)
        return version.__name__
    
    
def get_django_dispatch(service):
    def call_the_method(request,message,soap_action):
        for method in service.methods:
            if soap_action != method.soapAction:
                continue
            
            if isinstance(method.input,str): 
                element = service.schema.elements[method.input]
                input_object = element._type.parsexml(message,service.schema)
            else:
                input_object = method.input.parsexml(message,service.schema)
    
            return_object = method.function(request, input_object)
            try:
                tagname = uncapitalize(return_object.__class__.__name__)
                return_object.xml(tagname,namespace=service.schema.targetNamespace,
                                  elementFormDefault=service.schema.elementFormDefault,
                                  schema=service.schema)#Validation.
            except Exception, e:
                raise ValueError(e)
            
            if isinstance(method.output,str):
                tagname = method.output
            else:
                tagname = uncapitalize(return_object.__class__.__name__)
            return tagname,return_object
        raise ValueError("Method not found!")
    #-------------------------------------------------------------
    def django_dispatch(request):
        from django.http import HttpResponse
        import py2wsdl
        SOAP = service.version
        
        if request.method == "GET" and request.GET.has_key("wsdl"):
            wsdl = py2wsdl.generate_wsdl(service)
            return HttpResponse(wsdl,mimetype="text/xml")
        
        try:
            xml = request.raw_post_data
            envelope = SOAP.Envelope.parsexml(xml)
            message = envelope.Body.content()
            soap_action = SOAP.determin_soap_action(request)
            tagname,return_object = call_the_method(request, message, soap_action)
            soap_message = SOAP.Envelope.reponse(tagname,return_object)
            return HttpResponse(soap_message,content_type=SOAP.CONTENT_TYPE)
        except (ValueError,etree.XMLSyntaxError) as e:
            response = SOAP.get_error_response(SOAP.Code.CLIENT,str(e))
        except Exception, e:
            response = SOAP.get_error_response(SOAP.Code.SERVER,str(e))
        return HttpResponse(response, content_type=SOAP.CONTENT_TYPE)
    #-------------------------------------------------------------
    return django_dispatch
    
        
        

class SOAPError(Exception):
    pass
    
class Service(object):
    """Describes service aggregating informations required for dispatching 
    and WSDL generation. """ 
    def __init__(self,targetNamespace, location, schema, methods, 
                 version=SOAPVersion.SOAP11,name="Service"):
        """:param targetNamespace: string
           :param location: string, endpoint url.
           :param schema: xsd.Schema instance.
           :param methods: list of xsd.Methods"""
        self.name = name
        self.targetNamespace = targetNamespace
        self.location = location
        self.schema = schema
        self.methods = methods
        self.version = version
        
    def get_method(self, operationName):
        return filter(lambda m:m.operationName ==operationName, self.methods)[0]
            

class Stub(object):
    """Client stub. Handles only document style calls.""" 
    SERVICE = None
    
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        
    def _handle_response(self, method, response, content):
        SOAP = self.SERVICE.version
        envelope = SOAP.Envelope.parsexml(content)
        
        if envelope.Body.Fault:
            code,message = SOAP.parse_fault_message(envelope.Body.Fault)
            raise SOAPError("Fault Code:%s, Fault Message: %s" % (code,message))
        
        message = envelope.Body.content()
        
        if isinstance(method.output, str):
            element = self.SERVICE.schema.get_element_by_name(method.output)
            _type = element._type
        else:
            _type = method.output
            
        if self.SERVICE.schema:
            return _type.parsexml(message, self.SERVICE.schema)
        else:
            return _type.parsexml(message)
        
        
    def call(self, operationName, parameter):
        #Will raise: lxml.etree.XMLSyntaxError on validation problems.
        SOAP = self.SERVICE.version
        method = self.SERVICE.get_method(operationName)
        if isinstance(method.input,str):
            tagname = method.input
        else:
            tagname = uncapitalize(parameter.__class__.__name__)
        parameter.xml(tagname, 
                      schema=self.SERVICE.schema,
                      namespace=parameter.SCHEMA.targetNamespace,
                      elementFormDefault=parameter.SCHEMA.elementFormDefault)
        
        h = httplib2.Http()
        if self.username:
            h.add_credentials(self.username, self.password)
        
        method = self.SERVICE.get_method(operationName)    
        headers = SOAP.build_header(method.soapAction)    
        envelope = SOAP.Envelope.reponse(tagname,parameter)
    
        response, content = h.request(self.SERVICE.location, "POST",
             body=envelope, headers=headers)
        return self._handle_response(method, response, content)
        
        
        

        
                    
            
        
        
    