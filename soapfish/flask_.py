# -*- coding: utf-8 -*-

from __future__ import absolute_import

from soapfish.core import SOAPRequest
from soapfish.soap_dispatch import SOAPDispatcher


def flask_dispatcher(service, **dispatcher_kwargs):
    from flask import request, Response

    def flask_dispatch():
        soap_request = SOAPRequest(request.environ, request.data)
        soap_dispatcher = SOAPDispatcher(service, **dispatcher_kwargs)
        soap_response = soap_dispatcher.dispatch(soap_request)

        response = Response(soap_response.http_content)
        response.status_code = soap_response.http_status_code
        for header_key, value in soap_response.http_headers.items():
            response.headers[header_key] = value
        return response

    return flask_dispatch
