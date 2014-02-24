# -*- coding: utf-8 -*-


__all__ = ['NullHandler', 'urlparse', 'urlunparse']

import logging
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


import six
if six.PY3:
    from urllib.parse import urlparse, urlunparse
else:
    from urlparse import urlparse, urlunparse

