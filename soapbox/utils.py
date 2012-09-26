# -*- coding: utf-8 -*-
################################################################################

'''
'''

################################################################################
# Imports


import httplib2
import logging
import os

from urlparse import urlparse, urlunparse

from . import settings, xsd


################################################################################
# Globals


logger = logging.getLogger('soapbox')
logger.addHandler(logging.NullHandler())


################################################################################
# File Functions

################################################################################
# Exceptions
class CustomFaultValueError(ValueError):
    def __init__(self, error_string, complex_type_instance=None):
        '''
        complex_type_instance is an instance of a sub class of xsd.ComplexType.
        This is rendered in Fault return if this exception is raised
        '''
        super(CustomFaultValueError, self).__init__(error_string)
        self.complex_type_instance = complex_type_instance

def open_document(path):
    '''
    '''
    logger.info('Opening document \'%s\'...' % path)
    # Handle documents available on the Internet:
    if path.startswith('http:'):
        disable_validation = not os.path.exists(settings.CA_CERTIFICATE_FILE)
        http = httplib2.Http(
            ca_certs=settings.CA_CERTIFICATE_FILE,
            disable_ssl_certificate_validation=disable_validation,
            timeout=settings.REQUEST_TIMEOUT,
        )
        _, content = http.request(path)
        return content

    # Attempt to open the document from the filesystem:
    else:
        return open(path, 'r').read()


################################################################################
# Template Filters


def remove_namespace(full_typename):
    '''
    '''
    if not full_typename:
        return None
    return full_typename.split(':')[-1]


def capitalize(value):
    '''
    '''
    return value[0].upper() + value[1:]


def uncapitalize(value):
    '''
    '''
    if value == 'QName':
        return value
    return value[0].lower() + value[1:]


def get_get_type(xsd_namespaces):
    '''
    '''
    def get_type(full_typename):
        '''
        '''
        if not full_typename:
            return None
        typename = full_typename.split(':')
        if len(typename) < 2:
            typename.insert(0, None)
        ns, typename = typename
        if ns in xsd_namespaces:
            return 'xsd.%s' % capitalize(typename)
        else:
            return '\'%s\'' % capitalize(typename)
    return get_type


def use(usevalue):
    '''
    '''
    if usevalue == xsd.Use.OPTIONAL:
        return 'xsd.Use.OPTIONAL'
    elif usevalue == xsd.Use.REQUIRED:
        return 'xsd.Use.REQUIRED'
    elif usevalue == xsd.Use.PROHIBITED:
        return 'xsd.Use.PROHIBITED'
    else:
        raise ValueError


def url_regex(url):
    '''
    http://example.net/ws/endpoint --> ^ws/endpoint$
    '''
    o = urlparse(url)
    return r'^%s$' % o.path.lstrip('/')


def url_component(url, item):
    '''
    '''
    parts = urlparse(url)
    try:
        return getattr(parts, item)
    except AttributeError:
        raise ValueError('Unknown URL component: %s' % item)


def url_template(url):
    '''
    http://example.net/ws/endpoint --> %s/ws/endpoint
    '''
    o = list(urlparse(url))
    o[0:2] = ['%(scheme)s', '%(host)s']
    return urlunparse(o)


################################################################################
# Other Functions


def find_xsd_namespaces(nsmap):
    '''
    '''
    xsd_namespaces = [
        'http://www.w3.org/2000/10/XMLSchema',
        'http://www.w3.org/2001/XMLSchema',
    ]
    namespaces = []
    for key, value in nsmap.iteritems():
        if value in xsd_namespaces:
            namespaces.append(key)
    return namespaces


################################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
