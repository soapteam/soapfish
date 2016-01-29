# -*- coding: utf-8 -*-


__all__ = ['basestring', 'urlparse', 'urlunparse']

import six

if six.PY3:
    from urllib.parse import urlparse, urlunparse
else:
    from urlparse import urlparse, urlunparse

basestring = six.string_types
