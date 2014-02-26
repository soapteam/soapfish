from soapbox.soap_dispatch import SOAPDispatcher
from soapbox import py2wsdl

import django
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


class DjangoSoapboxRequest(object):
    def __init__(self, request):
        self.request = request
        self.method = request.method
        self.META = request.META


class DjangoSOAPDispatcher(SOAPDispatcher):
    def __init__(self, service):
        super(DjangoSOAPDispatcher, self).__init__(service)

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        if request.method == 'GET' and 'wsdl' in request.GET:
            wsdl = py2wsdl.generate_wsdl(self.service)
            return HttpResponse(wsdl, mimetype='text/xml')

        soapbox_request = DjangoSoapboxRequest(request)
        if django.VERSION < (1, 4):
            body_contents = request.raw_post_data
        else:
            body_contents = request.body
        soap_response = super(DjangoSOAPDispatcher, self).dispatch(soapbox_request, body_contents)
        django_response =  HttpResponse(
            soap_response.message,
            content_type=soap_response.content_type)
        django_response.status_code = soap_response.status
        return django_response
