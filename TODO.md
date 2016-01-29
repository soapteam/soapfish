To Do
=====

This project is very, very promising:

- It is focused on XML and SOAP/WSDL without any compromise. In an ideal world
  soapfish works with each and every syntax allowed by these technologies.
- It allows you to have a representation of arbitrary XML including support
  for XSD. Parse any XML described by a schema into a nice class-based tree
  (and the other way round: serialization is possible as well).
- Because soapfish supports only SOAP and no other remoting protocol (e.g.
  ReST-style APIs with JSON) the API is not tied to the lowest common
  denominator. You should be able implement any given WSDL.

Unfortunately we're not there yet.

This is a typical open source software and XML/SOAP is usually not perceived
as a fun project. So various users added some smaller features which they
needed but typically there are many incomplete implementations above the very
basic layer (the object model to represent XML/XSD programmatically).
On the upside that means there are a lot of ways to improve the code and your
contribution and make a big difference.

Here some bigger areas which need work:

- A much more comprehensive set of unit tests
- Implement support for additional web frameworks
- XSD schema generation (object graph to XSD file) has most of its logic in a
  very complex Jinja2 template which shows it limits. For example features like
  named xs:Elements with embedded anonymous ComplexTypes can not be serialized
  to XSD currently.
  However the code internally assumes that the class tree and the XSD
  representation contain the same information so this can lead to bugs.
- The XSD mapping is currently incomplete: Some types in schemas are not
  implemented at all (e.g. xs:date, xs:gYearMonth). Other types might not be
  parsed/serialized correctly. Also references to xs:elements are pretty
  incomplete right now.
- Generated code (e.g. WSDL handling or XSD mapping) usually has some syntax
  errors. Some of them are fixable on their own but often this is because of
  other missing features (see above). The output should be usable as
  scaffolding though.

Don't worry if the items on the list above seem to big for you. Just start out
with something small, write tests and contribute them. Even a small (failing)
unit test which demonstrates a current shortcoming is great.

You might also check out current skipped unit tests which usually represent
missing functionality (though these might not be ideal beginner projects - if
they were trivial to implement I would have done that already).

All these shortcomings and limitations exist only because of the lack of
time and/or awareness about certain XSD features. The goal of this library is
to fully implement XSD schemas and potentially SOAP/WSDL so patches (with tests)
are always welcome.

Specific Items
--------------

- Fix circular dependency of generated schema classes.

See the **TODO** markers in `soapfish/*.py` for a complete list.
