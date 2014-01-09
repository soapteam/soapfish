# -*- coding: utf-8 -*-

__all__ = ['NullHandler']

import logging
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
