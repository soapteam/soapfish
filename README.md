Soapfish
========

[![PyPI Version](https://img.shields.io/pypi/v/soapfish.svg)](https://pypi.org/project/soapfish/)
[![PyPI License](https://img.shields.io/pypi/l/soapfish.svg)](https://pypi.org/project/soapfish/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/soapfish.svg)](https://pypi.org/project/soapfish/)
[![PyPI Status](https://img.shields.io/pypi/status/soapfish.svg)](https://pypi.org/project/soapfish/)
[![PyPI Wheel](https://img.shields.io/pypi/wheel/soapfish.svg)](https://pypi.org/project/soapfish/)
[![PyPI Python Versions](https://img.shields.io/pypi/pyversions/soapfish.svg)](https://pypi.org/project/soapfish/)
[![PyPI Implementation](https://img.shields.io/pypi/implementation/soapfish.svg)](https://pypi.org/projects/soapfish/)

[![GitHub License](https://img.shields.io/github/license/soapteam/soapfish.svg)](https://github.com/soapteam/soapfish)
[![GitHub Version](https://img.shields.io/github/v/tag/soapteam/soapfish.svg?sort=semver)](https://github.com/soapteam/soapfish)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/soapteam/soapfish/test.svg)](https://github.com/soapteam/soapfish)

[![No Maintenance Intended](http://unmaintained.tech/badge.svg)](http://unmaintained.tech/)

**This project is not actively maintained. If you only need a dynamic client using a predefined WSDL rather than
generated code, it is recommended that you check out [Zeep](https://pypi.org/project/zeep/).**

Introduction
------------

Soapfish is a library to use SOAP services in Python. The server-side component can be used with Django, Flask, Pyramid
and other frameworks (including plain WSGI). The library can also be used to implement SOAP clients.

The library can help parsing/serializing a Python class model from/to XML and a bare-bones SOAP client.

Currently the project supports the following:

- SOAP 1.1 and 1.2
- WSDL 1.1
- WS-Addressing

Other notable features include:

- Support for Python 3.6+
- Licensed under the 3-clause BSD license
- Code generation utilities to get started quickly
- Parsing/serializing a Python class model from/to XML so you can easily work
  with XML even if you don't use SOAP at all.
