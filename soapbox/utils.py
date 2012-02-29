# -*- coding: utf-8 -*-
################################################################################

'''
'''

################################################################################
# Imports


from urlparse import urlparse

from . import xsd


################################################################################
# Functions


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


def removens(full_typename):
    '''
    '''
    if not full_typename:
        return None
    return full_typename.split(':')[-1]


def classyfiy(value):
    '''
    '''
    return value[0].upper() + value[1:]


def get_get_type(XSD_NAMESPACES):
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
        if ns in XSD_NAMESPACES:
            return 'xsd.%s' % classyfiy(typename)
        else:
            return '\'%s\'' % classyfiy(typename)
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


def find_xsd_namepsace(nsmap):
    '''
    '''
    namespaces = []
    for key, value in nsmap.iteritems():
        if value == 'http://www.w3.org/2001/XMLSchema' \
            or value == 'http://www.w3.org/2000/10/XMLSchema':
            namespaces.append(key)
    return namespaces


def urlcontext(url):
    '''
    http://example.net/ws/endpoint --> ^ws/endpoint$
    '''
    o = urlparse(url)
    return r'^%s$' % o.path.lstrip('/')


def uncapitalize(value):
    '''
    '''
    if value == 'QName':
        return value
    return value[0].lower() + value[1:]


################################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
