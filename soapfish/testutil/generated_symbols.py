# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import logging

__all__ = ['generated_symbols']

def generated_symbols(code_string):
    # imports not present in generated code
    from soapfish import xsd
    from soapfish.xsd import UNBOUNDED

    new_locals = dict(locals())

    try:
        # Let's trust our own code generation...
        exec(code_string, {'xsd': xsd}, new_locals)
    except Exception:
        logging.warning("Code could not be imported:\n%s", code_string)
        raise
    new_variables = set(new_locals).difference(locals())

    schema = None
    new_symbols = dict()
    for name in new_variables:
        symbol_ = new_locals[name]
        new_symbols[name] = symbol_
        if isinstance(symbol_, xsd.Schema):
            schema = symbol_
    return schema, new_symbols
