# -*- coding: utf-8 -*-


class SoapboxResponse(object):
    def __init__(self, content, soap_header=None):
        self.content = content
        self.soap_header = soap_header


class SoapboxRequest(object):
    def __init__(self, environ, content):
        self.environ = environ
        self.content = content
        self.soap_header = None
