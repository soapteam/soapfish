# -*- coding: utf-8 -*-
################################################################################

'''
'''

################################################################################
# Imports


import httplib2

from urlparse import urlparse

from . import xsd


################################################################################
# File Functions


def open_document(path):
    '''
    '''
    # Handle documents available on the Internet:
    if path.startswith('http:'):
        http = httplib2.Http()
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
    return value.capitalize()


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


def urlcontext(url):
    '''
    http://example.net/ws/endpoint --> ^ws/endpoint$
    '''
    o = urlparse(url)
    return r'^%s$' % o.path.lstrip('/')


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
