# -*- coding: utf-8 -*-

from datetime import timedelta as TimeDelta
import requests
import logging
import six

from . import namespaces as ns
from .compat import urlparse, urlunparse


logger = logging.getLogger('soapfish')


# --- File Functions ----------------------------------------------------------
def open_document(path):
    logger.info('Opening document \'%s\'...' % path)
    # Handle documents available on the Internet:
    if path.startswith('http:'):
        return requests.get(path).text

    # Attempt to open the document from the filesystem:
    else:
        return open(path, 'rb').read()


# --- Template Filters --------------------------------------------------------
def remove_namespace(full_typename):
    if not full_typename:
        return None
    return full_typename.split(':')[-1]


def capitalize(value):
    return value[0].upper() + value[1:]


def uncapitalize(value):
    if value == 'QName':
        return value
    return value[0].lower() + value[1:]


def get_get_type(xsd_namespaces):
    def get_type(full_typename, known_types = None):
        if not full_typename:
            return None
        typename = full_typename.split(':')
        if len(typename) < 2:
            typename.insert(0, None)
        ns, typename = typename
        if ns in xsd_namespaces:
            return 'xsd.%s' % capitalize(typename)
        else:
            if known_types is not None and typename in known_types:
                return "%s" % capitalize(typename)
            else:
                return "__name__ + '.%s'" % capitalize(typename)
    return get_type


def use(usevalue):
    from .xsd import Use
    if usevalue == Use.OPTIONAL:
        return 'xsd.Use.OPTIONAL'
    elif usevalue == Use.REQUIRED:
        return 'xsd.Use.REQUIRED'
    elif usevalue == Use.PROHIBITED:
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
    o[0:2] = ['{scheme}', '{host}']
    return urlunparse(o)


# --- Other Functions ---------------------------------------------------------
def find_xsd_namespaces(nsmap):
    xsd_namespaces = [
        ns.xsd2000,
        ns.xsd,
    ]
    namespaces = []
    for key, value in six.iteritems(nsmap):
        if value in xsd_namespaces:
            namespaces.append(key)
    return namespaces

def timezone_offset_to_string(offset):
    '''
    Returns a XSD-compatible string representation of a time zone UTC offset
    (timedelta).
    e.g. timedelta(hours=1, minutes=30) -> '+01:30'
    '''
    # Please note that this code never uses 'Z' for UTC but returns always the
    # full offset (which is completely valid as far as the XSD spec goes).
    # The main reason for that (besides slightly simpler code) is that checking
    # for "UTC" is more complicated than one might suspect. A common failure is
    # to check for a UTC offset of 0 and the absence of winter/summer time.
    # However there are time zones (e.g. Africa/Ghana) which satisfy these
    # criteria as well but are NOT UTC. In particular the local government may
    # decide to introduce some kind of winter/summer time while UTC is
    # guaranteed to have no such things.
    sign = '+' if (offset >= TimeDelta(0)) else '-'
    offset_seconds = abs((offset.days * 24 * 60 * 60) + offset.seconds)
    hours = offset_seconds // 3600
    minutes = (offset_seconds % 3600) // 60
    return '%s%02d:%02d' % (sign, hours, minutes)

