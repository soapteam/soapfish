import contextlib
import importlib
import logging
import os
import random
import string
import sys
import tempfile

__all__ = ['generated_symbols', 'import_code']


def generated_symbols(code):
    from soapfish import xsd  # import may not be generated.

    globals_ = {'xsd': xsd}
    globals_old = dict(globals_)

    try:
        # Let's trust our own code generation...
        exec(code, globals_)
    except Exception:
        logging.warning('Code could not be imported:\n%s', code)
        raise

    variables = globals_.keys() - globals_old.keys()

    schemas, symbols = [], {}
    for name in sorted(variables):
        symbol = globals_[name]
        symbols[name] = symbol
        if isinstance(symbol, xsd.Schema):
            schemas.append(symbol)
    return schemas, symbols


@contextlib.contextmanager
def import_code(code):
    with tempfile.TemporaryDirectory() as tmp_dir:
        name = 'import_code_' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        with open(os.path.join(tmp_dir, name) + '.py', 'w+b') as f:
            f.write(code)
        sys.path.append(tmp_dir)
        try:
            yield importlib.import_module(name)
        finally:
            sys.path.remove(tmp_dir)
