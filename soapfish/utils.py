# -*- coding: utf-8 -*-

import hashlib
import keyword
import logging
from datetime import datetime, timedelta

import requests
import six
from jinja2 import Environment, PackageLoader

from . import namespaces as ns

logger = logging.getLogger('soapfish')


# --- File Functions ----------------------------------------------------------
def open_document(path):
    if '://' in path:
        logger.info('Opening remote document: %s', path)
        return requests.get(path).content
    else:
        logger.info('Opening local document: %s', path)
        with open(path, 'rb') as f:
            return f.read()


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


def use(value):
    from . import xsd
    if value == xsd.Use.OPTIONAL:
        return 'xsd.Use.OPTIONAL'
    if value == xsd.Use.REQUIRED:
        return 'xsd.Use.REQUIRED'
    if value == xsd.Use.PROHIBITED:
        return 'xsd.Use.PROHIBITED'
    raise ValueError('Unknown value for use attribute: %s' % value)


def url_regex(url):
    '''
    http://example.net/ws/endpoint --> ^ws/endpoint$
    '''
    o = six.moves.urllib.parse.urlparse(url)
    return r'^%s$' % o.path.lstrip('/')


def url_component(url, item):
    parts = six.moves.urllib.parse.urlparse(url)
    try:
        return getattr(parts, item)
    except AttributeError:
        raise ValueError('Unknown URL component: %s' % item)


def url_template(url):
    '''
    http://example.net/ws/endpoint --> %s/ws/endpoint
    '''
    o = list(six.moves.urllib.parse.urlparse(url))
    o[0:2] = ['{scheme}', '{host}']
    return six.moves.urllib.parse.urlunparse(o)


def schema_name(obj, location=None):
    from . import xsdspec

    if location:
        value = location
    elif isinstance(obj, xsdspec.Schema):
        value = obj.targetNamespace
    elif isinstance(obj, xsdspec.Import):
        value = obj.namespace
    elif isinstance(obj, xsdspec.Include):
        value = obj.schemaLocation
    else:
        raise TypeError('Unable to generate schema name for %s.%s'
                        % (obj.__class__.__module__, obj.__class__.__name__))

    try:
        value = value.encode()
    except UnicodeEncodeError:
        pass

    # no cryptographic requirement here, so use md5 for fast hash:
    return hashlib.md5(value).hexdigest()[:5]


def get_rendering_environment(xsd_namespaces, module='soapfish'):
    '''
    Returns a rendering environment to use with code generation templates.
    '''
    from . import soap, xsd, wsdl

    def get_type(full_typename, known_types=None):
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

    env = Environment(
        extensions=['jinja2.ext.do', 'jinja2.ext.loopcontrols'],
        loader=PackageLoader('soapfish', 'templates'),
    )
    env.filters.update(
        capitalize=capitalize,
        max_occurs_to_code=lambda x: 'xsd.UNBOUNDED' if x is xsd.UNBOUNDED else str(x),
        remove_namespace=remove_namespace,
        type=get_type,
        url_component=url_component,
        url_regex=url_regex,
        url_template=url_template,
        use=use,
    )
    env.globals.update(
        SOAPTransport=soap.SOAP_HTTP_Transport,
        keywords=keyword.kwlist,
        get_by_name=wsdl.get_by_name,
        get_message_header=wsdl.get_message_header,
        get_message_object=wsdl.get_message_object,
        preamble={
            'module': module,
            'generated': datetime.now(),
        },
        schema_name=schema_name,
    )
    return env


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
    sign = '+' if (offset >= timedelta(0)) else '-'
    offset_seconds = abs((offset.days * 24 * 60 * 60) + offset.seconds)
    hours = offset_seconds // 3600
    minutes = (offset_seconds % 3600) // 60
    return '%s%02d:%02d' % (sign, hours, minutes)
