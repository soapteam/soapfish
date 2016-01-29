Soapfish
========

[![Travis](https://img.shields.io/travis/FelixSchwarz/soapfish/master.svg)](https://travis-ci.org/FelixSchwarz/soapfish)
[![PyPI](https://img.shields.io/pypi/v/soapfish.svg)](https://pypi.python.org/pypi/soapfish)
[![PyPI](https://img.shields.io/pypi/l/soapfish.svg)](https://pypi.python.org/pypi/soapfish)
[![PyPI](https://img.shields.io/pypi/dm/soapfish.svg)](https://pypi.python.org/pypi/soapfish)
[![PyPI](https://img.shields.io/pypi/pyversions/soapfish.svg)](https://pypi.python.org/pypi/soapfish)
[![PyPI](https://img.shields.io/pypi/status/soapfish.svg)](https://pypi.python.org/pypi/soapfish)
[![PyPI](https://img.shields.io/pypi/wheel/soapfish.svg)](https://pypi.python.org/pypi/soapfish)

Introduction
------------

Soapfish is a library to use SOAP services in Python. The server-side component
can be used with Django, Flask, Pyramid and other frameworks (including plain
WSGI). The library can also be used to implement SOAP clients.

The library can help parsing/serializing a Python class model from/to XML
and a bare-bones SOAP client.

Currently the project supports the following:

- SOAP 1.1 and 1.2
- WSDL 1.1
- WS-Addressing

Other notable features include:

- Support for Python 2.6, 2.7 and 3.3+
- Licensed under the 3-clause BSD license
- Code generation utilities to get started quickly
- Parsing/serializing a Python class model from/to XML so you can easily work
  with XML even if you don't use SOAP at all.
