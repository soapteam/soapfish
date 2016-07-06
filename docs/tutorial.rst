Tutorial
========

This tutorial assumes some understanding of XML, XSD, WSDL and SOAP.

Introduction
------------

The main purpose of this library is a neat implementation of the SOAP protocol,
but the `soapfish.xsd` module can used for any XML as it gives a means of
mapping XML to an object. The object description generally is similar to fields
in the Django ORM - the static fields that define instance fields. The main
difference would be that type is passed as first parameter, rather than being a
field e.g.

.. code-block:: python

    # Django:
    tail_number = models.CharField()

    # Soapfish:
    tail_number = xsd.Element(xsd.String)

`xsd.Element` reflects the nature of the field, elements are fields that will
be wrapped with tags. Other options are `xsd.Attribute`, `xsd.Ref` and
`xsd.ListElement`. For more detail see the documentation string for
`xsd.Element`. As SOAP, WSDL and XSD files are also XML documents the
`soapfish.xsd` module was also used to describe them. The descriptions are
located in `soapfish.xsdspec`, `soapfish.soap` and `soapfish.wsdl`. The
`soapfish.soap` module also provides dispatcher and client Stub.

Other elements included in this tool are translators, that can generate python
code from formal description or formal description from code. Relevant modules
include `soapfish.py2xsd`, `soapfish.xsd2py`, `soapfish.wsdl2py` and
`soapfish.py2wsdl`.

`soapfish.utils` mostly contains helper functions for Jinja2. Jinja2 is
templating engine used for code generation.

1. Working with XML
-------------------

The main building blocks are `xsd.ComplexType`, `xsd.Element`, `xsd.Attribute`
and the simple types defined in the `soapfish.xsd` module. `xsd.ComplexType` is
a class that can be extended to define custom types. The main methods defined
for types are `xml()` - translates object into XML - and `parsexml()` - builds
object from XML.

**Example 1: Rendering an object to XML**

.. code-block:: python

    from soapfish import xsd

    class Airport(xsd.ComplexType):
        type = xsd.Element(xsd.String)
        code = xsd.Element(xsd.String)

    airport = Airport()
    airport.type = 'IATA'
    airport.code = 'WAW'

    print(airport.xml('takeoff_airport'))

.. code-block:: xml

    <takeoff_airport>
      <type>IATA</type>
      <code>WAW</code>
    </takeoff_airport>

Note that `xml()` method takes one parameter - the name of the root tag.

**Example 2: Parsing XML to an object**

.. code-block:: python

    from soapfish import xsd

    class Airport(xsd.ComplexType):
         type = xsd.Element(xsd.String)
         code = xsd.Element(xsd.String)

    xml = '<takeoff_airport><type>IATA</type><code>WAW</code></takeoff_airport>'
    airport = Airport.parsexml(xml)

    print('Type: %s' % airport.type)
    print('Code: %s' % airport.code)

.. code-block:: text

    Type: IATA
    Code: WAW

**Example 3: Nested complex types with attributes**

.. code-block:: python

    from datetime import datetime
    from soapfish import xsd

    class Airport(xsd.ComplexType):
         type = xsd.Element(xsd.String)
         code = xsd.Element(xsd.String)

    class Flight(xsd.ComplexType):
        tail_number = xsd.Attribute(xsd.String)
        type = xsd.Attribute(xsd.Integer, use=xsd.Use.OPTIONAL)
        takeoff_airport = xsd.Element(Airport)
        takeoff_datetime = xsd.Element(xsd.DateTime, minOccurs=0)
        landing_airport = xsd.Element(Airport)
        landing_datetime = xsd.Element(xsd.DateTime, minOccurs=0)

    obj = Flight(tail_number='G-ABCD')
    obj.takeoff_airport = Airport(type='IATA', code='WAW')
    obj.landing_airport = Airport(type='ICAO', code='EGLL')
    obj.takeoff_datetime = datetime.now()

    print(obj.xml('flight'))

.. code-block:: xml

    <flight tail_number="G-ABCD">
      <takeoff_airport>
        <type>IATA</type>
        <code>WAW</code>
      </takeoff_airport>
      <takeoff_datetime>2011-05-06T11:11:23</takeoff_datetime>
      <landing_airport>
        <type>ICAO</type>
        <code>EGLL</code>
      </landing_airport>
    </flight>

2. Schema
---------

`xsd.Schema` is an object that aggregates all information stored in XSD file.
There two main use cases for this object. It can be used to generate an XSD
file or it can be generated from such file. For detail field description see
the documentation string for `xsd.Schema`. A schema instance is required for
validation and because SOAP webservice performs validation is required for
service configuration too.

2.1. Generating code from XSD file
''''''''''''''''''''''''''''''''''

`soapfish.py2xsd` generates a Python representation of an XML from an XSD file.

**Example:** `python -m soapfish.xsd2py examples/ops.xsd`

.. code-block:: python

    from soapfish import xsd

    class Pilot(xsd.String):
        enumeration = ['CAPTAIN', 'FIRST_OFFICER']

    class Airport(xsd.ComplexType):
        INHERITANCE = None
        INDICATOR = xsd.Sequence
        code_type = xsd.Element(xsd.String(enumeration=['ICAO', 'IATA', 'FAA']))
        code = xsd.Element(xsd.String)

    class Weight(xsd.ComplexType):
        INHERITANCE = None
        INDICATOR = xsd.Sequence
        value = xsd.Element(xsd.Integer)
        unit = xsd.Element(xsd.String(enumeration=['kg', 'lb']))

    class Ops(xsd.ComplexType):
        INHERITANCE = None
        INDICATOR = xsd.Sequence
        aircraft = xsd.Element(xsd.String)
        flight_number = xsd.Element(xsd.String)
        type = xsd.Element(xsd.String(enumeration=[
            'COMMERCIAL', 'INCOMPLETE', 'ENGINE_RUN_UP', 'TEST',
            'TRAINING', 'FERRY', 'POSITIONING', 'LINE_TRAINING']))
        takeoff_airport = xsd.Element(Airport)
        takeoff_gate_datetime = xsd.Element(xsd.DateTime, minOccurs=0)
        takeoff_datetime = xsd.Element(xsd.DateTime)
        takeoff_fuel = xsd.Element(Weight, minOccurs=0)
        takeoff_gross_weight = xsd.Element(Weight, minOccurs=0)
        takeoff_pilot = xsd.Element(Pilot, minOccurs=0)
        landing_airport = xsd.Element(Airport)
        landing_gate_datetime = xsd.Element(xsd.DateTime, minOccurs=0)
        landing_datetime = xsd.Element(xsd.DateTime)
        landing_fuel = xsd.Element(Weight, minOccurs=0)
        landing_pilot = xsd.Element(Pilot, minOccurs=0)
        destination_airport = xsd.Element(Airport, minOccurs=0)
        captain_code = xsd.Element(xsd.String, minOccurs=0)
        first_officer_code = xsd.Element(xsd.String, minOccurs=0)
        V2 = xsd.Element(xsd.Integer, minOccurs=0)
        Vref = xsd.Element(xsd.Integer, minOccurs=0)
        Vapp = xsd.Element(xsd.Integer, minOccurs=0)

    class Status(xsd.ComplexType):
        INHERITANCE = None
        INDICATOR = xsd.Sequence
        action = xsd.Element(xsd.String(enumeration=['INSERTED', 'UPDATED', 'EXISTS']))
        id = xsd.Element(xsd.Long)

    Schema = xsd.Schema(
        targetNamespace='http://flightdataservices.com/ops.xsd',
        elementFormDefault='unqualified',
        simpleTypes=[Pilot],
        attributeGroups=[],
        groups=[],
        complexTypes=[Airport, Weight, Ops, Status],
        elements = {'status': xsd.Element(Status), 'ops': xsd.Element(Ops)},
    )


Redirect the output to a python file: `python -m soapfish.xsd2py examples/ops.xsd > /tmp/ops.py`.

Now calling `python -m soapfish.py2xsd /tmp/ops.py` will generate the
equivalent XSD from the Python code. The `soapfish.xsd2py` script expects a
schema instance to be defined in global scope called "Schema", in a way similar
to one in generated code.

3. Web Service
--------------

When a WSDL file is provided server or client code can be generated using the
`soapfish.wsdl2py` script. If not, it is advised to write code first a then use
a browser to request the specification. Accessing your service with the query
string `?wsdl` appended will give the current WSDL with XSD embedded.

3.1. Generating code from WSDL file
'''''''''''''''''''''''''''''''''''

`soapfish.wsdl2py` can generate either client or server code:

    `python -m soapfish.wsdl2py -c examples/ops.wsdl`
    `python -m soapfish.wsdl2py -s examples/ops.wsdl`

3.1.1. Server
^^^^^^^^^^^^^

**Example:** `python -m soapfish.wsdl2py -s examples/ops.wsdl`

.. code-block:: python

    # XML Schema Removed...

    PutOps_method = xsd.Method(
        function=PutOps,
        soapAction='http://www.example.com/ws/ops/PutOps',
        input='ops',      # Pointer to Schema.elements
        output='status',  # Pointer to Schema.elements
        operationName='PutOps',
    )

    SERVICE = soap.Service(
        targetNamespace='http://www.example.com/ops.wsdl',
        location='http://www.example.com/ws/ops',
        schema=Schema,
        methods=[PutOps_method],
    )


Generated code includes methods descriptions, service description, dispatcher
and Django `urls.py` binding.

`xsd.Method` describes one method for service (that can consist from more than
one method). Methods give dispatcher informations required for method
distinction - `soapAction` and `operationName`, and `function` to call on
incoming SOAP message. For detail field meaning see the documentation string
for `xsd.Method`.

`SERVICE` aggregates all informations required for WSDL generation and correct
dispatching. `get_django_dispatch()` returns a function binded to `SERVICE`
that pointed from `urls.py` will call appropriate function on incoming SOAP
message. The called function, in this example `PutOps`, is expected to return
object from XSD that could be translated to correct and valid response - for
this example this would be a `Status` instance.

URLs binding it is commented out, paste this code into your `urls.py` and
change <fill the module path> to point file where to code was generated.

3.1.2. Client
^^^^^^^^^^^^^

**Example:** `python -m soapfish.wsdl2py -c examples/ops.wsdl`

.. code-block:: python

    # XML Schema Removed...

    PutOps_method = xsd.Method(
        soapAction='http://www.example.com/ws/ops/PutOps',
        input='ops',      # Pointer to Schema.elements
        output='status',  # Pointer to Schema.elements
        operationName='PutOps',
    )

    SERVICE = soap.Service(
        targetNamespace='http://www.example.com/ops.wsdl',
        location='http://www.example.com/ws/ops',
        schema=Schema,
        methods=[PutOps_method],
    )

    class ServiceStub(soap.Stub):
        SERVICE = SERVICE

        def PutOps(self, ops):
            return self.call('PutOps', ops)


`ServiceStub` is a proxy object that defines methods available on the remote
webservice. Calling one of those methods - in the example there is only one -
`PutOps` - will produce SOAP call to remote server defined in `SERVICE`. The
methods will return appropriate object from XSD description or raise an
exception on encountering any problems.

For more examples see `examples/client.py`

3.2. Building Webservice
''''''''''''''''''''''''

The build a webservice we need to define few things:

 * Classes that would be send via SOAP
 * Schema instance that aggregates all classes with name space etc.
 * Web service functions and all related informations
 * Service instance to put everything together
 * Binding to a URL

Lets build the stock web service that will give a stock price for provided
company code and datetime.

3.2.1. Stack classes
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    class GetStockPrice(xsd.ComplexType):
        company = xsd.Element(xsd.String, minOccurs=1)
        datetime = xsd.Element(xsd.DateTime)

    class StockPrice(xsd.ComplexType):
        price = xsd.Element(xsd.Integer)

    Schema = xsd.Schema(
        targetNamespace='http://code.google.com/p/soapfish/stock.xsd',  # should be unique, can be any string.
        complexTypes=[GetStockPrice, StockPrice],
        elements={
            'getStockPrice': xsd.Element(GetStockPrice),
            'stockPrice': xsd.Element(StockPrice),
        },
    )

Note the elements in schema - for this version it is required to create an
element of a specific type and use its string element name as input/output in
Service definitions. WSDL specifications allows also direct use of the type,
which is not covered yet.

3.2.2. Method definition
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    def get_stock_price(request, gsp):
        print(gsp.company)
        return StockPrice(price=139)

    get_stock_price_method = xsd.Method(
        function=get_stock_price,
        soapAction='http://code.google.com/p/soapfish/stock/get_stock_price',
        input='getStockPrice',
        output='stockPrice',
        operationName='GetStockPrice',
    )


3.2.3. Putting it all together
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    SERVICE = soap.Service(
        targetNamespace='http://code.google.com/p/soapfish/stock.wsdl',
        location='http://127.0.0.1:8000/stock',  # where request should be sent.
        schema=Schema,
        methods=[get_stock_price_method],
    )

.. code-block:: python

    from wsgiref.simple_server import make_server
    from soapfish import soap_dispatch
    from service_gen import SERVICE

    dispatcher = soap_dispatch.SOAPDispatcher(SERVICE)
    app = soap_dispatch.WsgiSoapApplication({'/ChargePoint/services/chargePointService': dispatcher})

    print('Serving HTTP on port 8000...')
    httpd = make_server('', 8000, app)
    httpd.serve_forever()

Now requesting `http://127.0.0.1:8000/stock?wsdl` will give service specification and SOAP messages like:

.. code-block:: xml

    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:stoc="http://code.google.com/p/soapfish/stock.xsd">
      <soapenv:Header/>
      <soapenv:Body>
        <stoc:getStockPrice>
          <company>Google</company>
          <datetime>2010-08-20T21:39:59</datetime>
        </stoc:getStockPrice>
      </soapenv:Body>
    </soapenv:Envelope>

can be sent to http://127.0.0.1:8000/stock.

*The full working example can be found in examples/stock.*
