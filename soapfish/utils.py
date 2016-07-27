# -*- coding: utf-8 -*-

import hashlib
import itertools
import keyword
import logging
import os
from datetime import datetime, timedelta

import requests
import six
from jinja2 import Environment, PackageLoader

from . import namespaces as ns

logger = logging.getLogger('soapfish')


# --- File Functions ----------------------------------------------------------
def resolve_location(path, cwd):
    if '://' in path:
        path = location = path
        cwd = None
    else:
        path = os.path.join(cwd, path)
        location = os.path.relpath(path, cwd)
        cwd = os.path.dirname(path)
    return path, cwd, location


def open_document(path):
    if '://' in path:
        logger.info('Opening remote document: %s', path)
        return requests.get(path).content
    else:
        logger.info('Opening local document: %s', path)
        with open(path, 'rb') as f:
            return f.read()


# --- Template Filters --------------------------------------------------------
def remove_namespace(qname):
    return qname.split(':')[-1] if qname else None


def uncapitalize(value):
    if value == 'QName':
        return value
    return value[0].lower() + value[1:]


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


def schema_select(schemas, elements):
    selected = None
    elements = [remove_namespace(x) for x in elements]
    for schema in schemas:
        if all(schema.get_element_by_name(x) for x in elements):
            selected = schema
            break
    return selected


def get_rendering_environment(xsd_namespaces, module='soapfish'):
    '''
    Returns a rendering environment to use with code generation templates.
    '''
    from . import soap, xsd, xsdspec, wsdl

    def capitalize(value):
        return value[0].upper() + value[1:]

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
        o = six.moves.urllib.parse.urlparse(url)
        return r'^%s$' % o.path.lstrip('/')

    def url_component(url, item):
        parts = six.moves.urllib.parse.urlparse(url)
        try:
            return getattr(parts, item)
        except AttributeError:
            raise ValueError('Unknown URL component: %s' % item)

    def url_template(url):
        o = list(six.moves.urllib.parse.urlparse(url))
        o[0:2] = ['{scheme}', '{host}']
        return six.moves.urllib.parse.urlunparse(o)

    def get_type(obj, known_types=None):
        if isinstance(obj, (xsdspec.Attribute, xsdspec.Element)):
            if obj.ref:
                qname = obj.ref
            elif obj.type:
                qname = obj.type
            elif obj.simpleType:
                # FIXME: Determine how to handle embedded types...
                raise NotImplementedError('Unable to handle embedded type.')
        elif isinstance(obj, (xsdspec.Extension, xsdspec.Restriction)):
            if obj.base:
                qname = obj.base
        elif isinstance(obj, six.string_types):
            qname = obj

        if not qname:
            raise ValueError('Unable to determine type of %s' % obj)

        qname = qname.split(':')
        if len(qname) < 2:
            qname.insert(0, None)
        ns, name = qname

        if ns in xsd_namespaces:
            return 'xsd.%s' % capitalize(name)
        elif known_types is not None and name in known_types:
            return '%s' % capitalize(name)
        else:
            return "__name__ + '.%s'" % capitalize(name)

    keywords = set(keyword.kwlist + ['False', 'None', 'True'])

    env = Environment(
        extensions=['jinja2.ext.do', 'jinja2.ext.loopcontrols'],
        loader=PackageLoader('soapfish', 'templates'),
    )
    env.filters.update(
        capitalize=capitalize,
        fix_keyword=lambda x: '_%s' % str(x) if str(x) in keywords else str(x),
        max_occurs=lambda x: 'xsd.UNBOUNDED' if x is xsd.UNBOUNDED else str(x),
        remove_namespace=remove_namespace,
        type=get_type,
        url_component=url_component,
        url_regex=url_regex,
        url_template=url_template,
        use=use,
    )
    env.globals.update(
        SOAPTransport=soap.SOAP_HTTP_Transport,
        keywords=keywords,
        get_by_name=wsdl.get_by_name,
        get_message_header=wsdl.get_message_header,
        get_message_object=wsdl.get_message_object,
        preamble={
            'module': module,
            'generated': datetime.now(),
        },
        schema_name=schema_name,
        schema_select=schema_select,
    )
    return env


# --- Other Functions ---------------------------------------------------------
def find_xsd_namespaces(xml):
    nsmap = xml.nsmap.copy()
    for x in xml.xpath('//*[local-name()="schema"]'):
        nsmap.update(x.nsmap)
    return set(k for k, v in six.iteritems(nsmap) if v in (ns.xsd, ns.xsd2000))


def walk_schema_tree(schemas, callback, seen=None):
    if seen is None:
        seen = {}
    for schema in schemas:
        for item in itertools.chain(schema.imports, schema.includes):
            if item.location not in seen:
                seen[item.location] = callback(item)
                walk_schema_tree([item], callback, seen)
    return seen


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
