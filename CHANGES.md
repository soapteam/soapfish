Changes
=======

0.6.0 (2020-??-??)
------------------

Project has been renamed to `soapfish` to distinguish it from the legacy
`soapbox` project and allow for publishing the project on PyPI. Note that the
rename effectively makes it backwards incompatible with previous releases due
to API breakage.

Due to lack of time to maintain the original `soapbox` project, `soapbox` been
retired by Flight Data Services who now contribute to and recommend the use of
the `soapfish` fork.

- **Security:**
  - Fixed potential security issue - pattern restrictions were not applied correctly
- **Features:**
  - Add support for xsd.date (date range currently limited by datetime.date)
  - Add support relative schema paths (#49)
  - Add support to string restrictions length, minLength, maxLength, whiteSpace (#67)
  - Add support for choice indicator in ComplexTypes (#39)
    - Fixes validation of matching XML documents - previously sequences were always assumed - and code generation from WSDL/XSD.
    - _Patch contributed by Martin Mrose, tests written by Felix Schwarz_
  - Implemented a dispatcher for Flask (#53)
  - Implement service.route function to avoid changes to generated code (#68)
  - Changed to use `requests` instead of `httplib2`.
  - Added support for multiple inline schema imports and includes.
  - Added support for import of other WSDL documents.
  - Support for reordering of schema imports and includes and handle circular imports.
- **Bug Fixes:**
  - Make xsd.Decimal field accept Python Decimal (#52)
  - Fix relative imports with remote files. (#96)
  - Schema validation now also uses imported schemas correctly
  - Various fixes for `wsdl2py` and `xsd2py` when using Python 3
  - Fix exception in `SOAPDispatcher` when a handler does not return a `SOAPResponse`
  - Fix bad WSDL generation due to unresolved type references
  - Correctly apply pattern restrictions for simple types
  - Pattern restriction was not correctly serialized when generating schemas
  - Omit `minOccurs=1` and `maxOccurs=1` in `xsd2py` as these are the default.
    (The latter produces invalid code because `xsd.Element` doesn't support it.)
  - Restored ability to validate parsed XML using a soapfish schema in `ComplexType`
  - Fixed WSDL classes to more closely match the WSDL specifications.
  - Fixed WSDL classes to correctly define SOAP extensibility elements.
  - Removed reverse references from WSDL classes.
  - Fixed query string handling in dispatch to be more robust.
  - Support importing documents over HTTPS.
  - Fixed detection of XML schema namespaces.
  - Attempts to fix handling of remote vs local imports.
- **Miscellaneous:**
  - Renamed `SoapboxRequest` and `SoapboxResponse` to `SOAPRequest` and `SOAPResponse` respectively.
  - Support Python 3.6+, Django 1.11, 2.2 & 3.0, and Flask 1.0.0+
  - Improved testing against different versions of Python, Django & Flask.
  - Improved entry points for generation scripts - additional flags, etc.
  - Moved to using an external dependency for `iso8601`

0.5.1 (2014-06-12)
------------------

- **Miscellaneous:**
  - Downgrade log level on soap action discovery.

0.5.0 (2014-06-12)
------------------

- **Miscellaneous:**
  - Make elements inherit from schema namespace
  - Better logging in soap/stub
  - soap12: Quotes around action in HTTP header

0.4.0 (2014-05-06)
------------------

Project forked by Felix Schwarz as `soapbox-bsd` due to licensing incompatibilities.

Flight Data Services started using the GPL-incompatible OSL for the `soapbox`
project. This fork is based on the last `soapbox` commit still using the
original 3-clause BSD license (7d3516fe).  Later on the fork received
significant contributions from Thomas Recouvreux and Xavier Fernandez
(Polyconseil).

- **Features:**
  - Added support for SOAP 1.2 and WSDL 1.2
  - Added support for WS-Addressing
  - Added support for fault actors (Damian Powązka)
  - Added support for Django >= 1.4
  - Added compatibility with Python 3
  - Added framework-agnostic SOAP dispatcher to support virtually any web framework.
- **Bug Fixes:**
  - Preserve `elementFormDefault` attribute in Schema
  - Many bug fixes for code generation and XML rendering
- **Miscellaneous:**
  - Ability to use custom SOAP headers
  - Middleware stack to hook into SOAP request processing
  - Better handling of invalid SOAP requests, e.g. missing bodies, invalid actions.

0.3.2 (2012-03-09)
------------------

- **Miscellaneous:**
  - Initial support for variable URL scheme and host
  - Test suite executes

0.3.1 (2012-03-08)
------------------

- **Miscellaneous:**
  - SSL certificate verification

0.3.0 (2012-03-02)
------------------

- **Features:**
  - Add option to disable schema validation on parsing:
    - Set `xsd.VALIDATE_ON_PARSE` to `False`.
  - Added some initial logging support:
    - Request logging available at when level set to DEBUG.
- **Bug Fixes:**
  - Allow unicode as a valid type for strings.
  - Check for Python keywords and prefix with underscore.
- **Miscellaneous:**
  - Python code templates now loaded from external files.
  - Generated code is now much cleaner.
  - Generated code is now timestamped.
  - Code tidying as reported by pyflakes and pep8.
  - Fixed a number of typographical errors.
  - Various name improvements to functions.
  - Updated .hgignore
- **Known Issues:**
  - Generated schema classes can be circular referencing.
