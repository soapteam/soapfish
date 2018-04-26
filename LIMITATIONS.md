Limitations
===========

xsd.Ref() is not serialized
---------------------------

XML schema references are not serialized. Below is an example of code that does not generate a valid schema:

```python
from lxml import etree
from soapfish import py2xsd, xsd

class Person(xsd.Group):
    name = xsd.Element(xsd.String)
    surname = xsd.Element(xsd.String)

class Job(xsd.ComplexType):
    title = xsd.Element(xsd.String)
    person = xsd.Ref(Person)

schema = xsd.Schema(
    imports=[],
    targetNamespace='http://example.com/ws/spec',
    elementFormDefault='qualified',
    simpleTypes=[],
    attributeGroups=[],
    groups=[],
    complexTypes=[],
    elements={'job': xsd.Element(Job())},
)

print(etree.tostring(py2xsd.generate_xsd(schema), pretty_print=True))
```

Incorrect XML Schema:

```xml
<xsd:schema xmlns:sns="http://example.com/ws/spec" xmlns:xsd="http://www.w3.org/2001/XMLSchema" targetNamespace="http://example.com/ws/spec" elementFormDefault="qualified">
  <xsd:element name="job">
    <xsd:complexType>
      <xsd:sequence>
        <xsd:element name="title" type="xsd:string" minOccurs="1" nillable="false"/>
      </xsd:sequence>
    </xsd:complexType>
  </xsd:element>
</xsd:schema>
```

Expected XML Schema:

```xml
<xsd:schema xmlns:site="http://example.com/ws/spec" xmlns:xs="http://www.w3.org/2001/XMLSchema" targetNamespace="http://example.com/ws/spec" elementFormDefault="qualified">
  <xsd:element name="person">
    <xsd:complexType>
      <xsd:sequence>
        <xsd:element name="name" type="xs:string"/>
        <xsd:element name="surname" type="xs:string"/>
      </xsd:sequence>
    </xsd:complexType>
  </xsd:element>
  <xsd:element name="job">
    <xsd:complexType>
      <xsd:sequence>
        <xsd:element name="title" type="xs:string" minOccurs="1" nillable="false"/>
        <xsd:element ref="site:person"/>
      </xsd:sequence>
    </xsd:complexType>
  </xsd:element>
</xsd:schema>
```

Valid XML for Expected Schema:

```xml
<?xml version="1.0" encoding="utf-8" standalone="no"?>
<job xmlns="http://example.com/ws/spec">
  <title>Software Developer</title>
  <person>
    <name>Joe</name>
    <surname>Bloggs</surname>
  </person>
</job>
```

XSDDate does not support full date range
----------------------------------------

The XML schema specification does not limit the range of dates representable by
`xs:date`.  For example, the values `-2000-03-10` and `20000-04-20` are valid
as far `xs:date` is concerned. Currently `soapfish.xsd_types.XSDDate` is
subclassing Python's standard library `datetime.date` which has a much more
narrow definition.

Very likely the best solution is to back our implementation with an alternative
date implementation such as [`mxDateTime`](https://pypi.org/project/egenix-mx-base/)
which seems to represent all possible values from `xs:date`. As `mxDateTime`
currently (2014-11-13) uses compiled components (making it harder to install in
some environments) and does not support Python 3 this should likely be an
optional dependency (if at all).
