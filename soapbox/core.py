# -*- coding: utf-8 -*-


class SoapboxResponse(object):
    def __init__(self, content, soap_header=None):
        self.content = content
        self.soap_header = soap_header


class SoapboxRequest(object):
    def __init__(self, environ, content):
        self.environ = environ
        self.content = content
        self.dispatcher = None
        self.soap_header = None
        self.soap_body = None
        self.method = None


class SOAPError(Exception):
    def __init__(self, code, message, actor=None):
        super(SOAPError, self).__init__(code, message, actor)
        self.code = code
        self.message = message
        self.actor = actor

    def __str__(self):
        return "(%s) %s, actor=%s" % (self.code, self.message, self.actor)
