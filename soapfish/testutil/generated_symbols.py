# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import logging

import six

__all__ = ['generated_symbols']


def generated_symbols(code):
    from soapfish import xsd  # import may not be generated.

    globals_ = {'xsd': xsd}
    globals_old = dict(globals_)

    try:
        # Let's trust our own code generation...
        six.exec_(code, globals_)
    except Exception:
        logging.warning('Code could not be imported:\n%s', code)
        raise

    variables = set(globals_).difference(globals_old)

    schemas, symbols = [], {}
    for name in sorted(variables):
        symbol = globals_[name]
        symbols[name] = symbol
        if isinstance(symbol, xsd.Schema):
            schemas.append(symbol)
    return schemas, symbols
