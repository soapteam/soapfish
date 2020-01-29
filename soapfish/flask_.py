from .core import SOAPRequest
from .soap_dispatch import SOAPDispatcher

__all__ = ['flask_dispatcher']


def flask_dispatcher(service, **dispatcher_kwargs):
    from flask import request, Response

    def flask_dispatch():
        soap_request = SOAPRequest(request.environ, request.data)
        soap_request._original_request = request
        soap_dispatcher = SOAPDispatcher(service, **dispatcher_kwargs)
        soap_response = soap_dispatcher.dispatch(soap_request)

        response = Response(soap_response.http_content)
        response.status_code = soap_response.http_status_code
        for k, v in soap_response.http_headers.items():
            response.headers[k] = v
        return response

    return flask_dispatch
