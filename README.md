soapfish
===========

[![Build Status](https://travis-ci.org/FelixSchwarz/soapfish.png?branch=master)](https://travis-ci.org/FelixSchwarz/soapfish)


Introduction
------------

soapfish is a library to use SOAP services in Python. The server-side component
can be used with Pyramid, Django and other frameworks (including plain WSGI).
The library can also be used to implement SOAP clients with httplib2 (and
using another HTTP request library such as requests should only require
about 20-30 lines of code).

The library can also help parsing/serializing a Python class model from/to XML
and a bare-bones SOAP client.

The project aims to support any SOAP service. Therefore the code supports:

- SOAP 1.1 and 1.2
- WSDL 1.1 and 1.2
- WS-Addressing


Other notable features:

- support for Python 2.6+2.7 and Python 3
- code generation utilities to get started quickly
- parsing/serializing a Python class model from/to XML so you can easily work
  with XML even if you don't use SOAP at all.
- licensed under the 3-clause BSD license


The main contributors were Damian Powązka, Flight Data Services,
Thomas Recouvreux and Xavier Fernandez (Polyconseil) and
Felix Schwarz (sponsored by Rechenzentrum für Berliner Apotheken Stein & Reichwald GmbH).

