# -*- coding: utf-8 -*-

from __future__ import absolute_import

from soapfish.core import SOAPRequest
from soapfish.soap_dispatch import SOAPDispatcher

__all__ = ['django_dispatcher']

class DjangoEnvironWrapper(object):
    def __init__(self, environ):
        self.environ = environ

    def get(self, name, default=None):
        cgi_name = 'HTTP_'+name
        for key in (name, cgi_name):
            if key in self.environ:
                return self.environ[key]
        return default

def django_dispatcher(service, **dispatcher_kwargs):
    import django
    from django.http import HttpResponse
    from django.views.decorators.csrf import csrf_exempt

    def django_dispatch(request):
        body = request.body
        soap_request = SOAPRequest(DjangoEnvironWrapper(request.environ), body)
        soap_dispatcher = SOAPDispatcher(service, **dispatcher_kwargs)
        soap_response = soap_dispatcher.dispatch(soap_request)

        response = HttpResponse(soap_response.http_content)
        response.status_code = soap_response.http_status_code
        for header_key, value in soap_response.http_headers.items():
            response[header_key] = value
        return response
    return csrf_exempt(django_dispatch)
