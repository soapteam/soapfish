# -*- coding: utf-8 -*-


__all__ = ['SOAPError', 'SOAPRequest', 'SOAPResponse']


class SOAPError(Exception):
    def __init__(self, code, message, actor=None):
        super(SOAPError, self).__init__(code, message, actor)
        self.code = code
        self.message = message
        self.actor = actor

    def __str__(self):
        return "(%s) %s, actor=%s" % (self.code, self.message, self.actor)


class SOAPResponse(object):
    def __init__(self, soap_body, soap_header=None, http_status_code=200, http_content=None, http_headers=None):
        self.soap_header = soap_header
        self.soap_body = soap_body
        self.http_status_code = 200
        self.http_headers = {} if http_headers is None else http_headers
        self.http_content = http_content


class SOAPRequest(object):
    def __init__(self, environ, http_content):
        self.environ = environ
        self.http_content = http_content
        self.soap_header = None
        self.soap_body = None
        self.dispatcher = None
        self.method = None
