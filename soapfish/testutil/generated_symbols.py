# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import contextlib
import logging
import os
import random
import shutil
import six
import string
import sys
import tempfile

try:
    import importlib
except ImportError:
    importlib = None

__all__ = ['generated_symbols', 'import_code']


def generated_symbols(code):
    from soapfish import xsd  # import may not be generated.

    globals_ = {'xsd': xsd}
    globals_old = dict(globals_)

    try:
        # Let's trust our own code generation...
        six.exec_(code, globals_)
    except Exception as ex:
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


@contextlib.contextmanager
def import_code(code):
    code_module = None
    tmp_dir = None
    try:
        if tmp_dir is None:
            tmp_dir = tempfile.mkdtemp()
        module_name = "import_code_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        with open(os.path.join(tmp_dir, module_name) + ".py", 'w+b') as f:
            f.write(code)
        sys.path.append(tmp_dir)
        if importlib:
            code_module = importlib.import_module(module_name)
        else:
            code_module = __import__(module_name, globals(), {})  # XXX: Python 2.6
        yield code_module
    finally:
        if code_module is not None:
            del code_module
        if tmp_dir:
            if tmp_dir in sys.path:
                sys.path.remove(tmp_dir)
            shutil.rmtree(tmp_dir, ignore_errors=True)
