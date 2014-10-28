Tutorial
========

This tutorial assumes some understanding of XML, XSD, WSDL and SOAP.

Introduction
------------

The main purpose of this library is neat implementation of SOAP protocol,
but xsd package can used for any XML as it gives means of mapping XML
to object. The object description generally is similar to Django database models - the static fields that define instance fields. The main difference would be that type is passed as first parameter, rather then being a field e.g

.. code-block:: python

    # in Django
    Django: tail_number = models.CharField()

    # in soapfish
    soapfish: tail_number = xsd.Element(xsd.String)

xsd.Element reflects the nature of the field, elements are fields that
will be wrapped with tag, other options are xsd.Attribute, xsd.Ref and 
xsd.ListElement. For more detail see xsd.Element pydoc.As SOAP, WSDL and XSD files are also XMLs the xsd package was also used to describe them. The descriptions are located in xsdspec.py, soap.py
and wsdl.py. soap package also provides dispatcher and client Stub.

Other elements included in this tool are translators, that can generate python code from formal description or formal description from code. Related files: py2xsd.py, xsd2py.py, wsdl2py.py, py2wsdl.py.

utils.py is mostly jinja2 helper functions. jinja2 is templating engine used for code generation.


1. Working with XML
-------------------

The main building blocks are xsd.ComplexType, xsd.Element, xsd.Attribute and simple types defined in xsd package. xsd.ComplexType is a parent to extend to define own type. Main methods for types are xml - translates object into XML, and parsexml builds object from XML.

.. code-block:: python

    #Example 1. Rendering object to XML.
    from soapfish import xsd

    class Airport(xsd.ComplexType):
        type = xsd.Element(xsd.String)
        code = xsd.Element(xsd.String)

    airport = Airport()
    airport.type = "IATA"
    airport.code = "WAW"
    print airport.xml("takeoff_airport")

Note that xml method takes one parameter  - root tag name.

.. code-block:: python

    #Example 2. Parsing XML to object.
    from soapfish import xsd
    class Airport(xsd.ComplexType):
         type = xsd.Element(xsd.String)
         code = xsd.Element(xsd.String)
    
    XML = """<takeoff_airport>
      <type>IATA</type>
      <code>WAW</code>
    </takeoff_airport>"""
    
    airpport = Airport.parsexml(XML)
    print "Type:", airport.type#prints Type: IATA
    print "Code:", airport.code#Code: WAW


.. code-block:: python

    #Example 3. Nested ComplexTypes with attributes.
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
        
    flight = Flight(tail_number="LN-KKA")#Constructor handles field inititailization.
    flight.takeoff_airport = Airport(type="IATA", code="WAW")
    flight.landing_airport = Airport(type="ICAO", code="EGLL")
    
    print flight.xml("flight")
    #datetime field types will accept, datetime object or string,
    #that parses correctly to such object.
    flight.takeoff_datetime = datetime.now()
    print flight.xml("flight") 


will produce

.. code-block:: python

    <flight tail_number="LN-KKA">
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

xsd.Schema is an object that aggregates all informations stored in XSD file. There two main use cases for this object. It can be used to generate XSD file or it can be generated from such file. For detail field description see: xsd.Schema pydoc. Schema instance is required for validation and because SOAP webservice performs validation is required for service configuration too: See documentation Defining webservice.

2.1 Generating code from XSD file
'''''''''''''''''''''''''''''''''

py2xsd.py generates Python representation of XML from XSD file.
Example: 
{{{xsd2py.py examples\ops.xsd}}} 

will generate:

.. code-block:: python

    from soapfish import xsd
    
    class Pilot(xsd.String):
        enumeration = [ "CAPTAIN",  "FIRST_OFFICER", ]
    
    class Airport(xsd.ComplexType):
        INHERITANCE = None
        INDICATOR = xsd.Sequence
        code_type = xsd.Element(xsd.String( enumeration =
        [ "ICAO", "IATA", "FAA",]) )
        code = xsd.Element(xsd.String)
    
    
    class Weight(xsd.ComplexType):
        INHERITANCE = None
        INDICATOR = xsd.Sequence
        value = xsd.Element(xsd.Integer)
        unit = xsd.Element(xsd.String( enumeration =
        [ "kg", "lb",]) )
    
    
    class Ops(xsd.ComplexType):
        INHERITANCE = None
        INDICATOR = xsd.Sequence
        aircraft = xsd.Element(xsd.String)
        flight_number = xsd.Element(xsd.String)
        type = xsd.Element(xsd.String( enumeration =
        [ "COMMERCIAL", "INCOMPLETE", "ENGINE_RUN_UP", "TEST", "TRAINING", "FERRY",
    "POSITIONING", "LINE_TRAINING",]) )
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
        action = xsd.Element(xsd.String( enumeration =
        [ "INSERTED", "UPDATED", "EXISTS",]) )
        id = xsd.Element(xsd.Long)
    
    Schema = xsd.Schema(
        targetNamespace = "http://flightdataservices.com/ops.xsd",
        elementFormDefault = "unqualified",
        simpleTypes = [ Pilot,],
        attributeGroups = [],
        groups = [],
        complexTypes = [ Airport, Weight, Ops, Status,],
        elements = {  "status":xsd.Element(Status), "ops":xsd.Element(Ops),})


Let redirect output to the python file.
{{{xsd2py.py examples\ops.xsd > tmp\ops.py}}}.
Now calling {{{py2xsd.py tmp\ops.py}}} will generate equivalent XSD from Python code. xsd2py script expects schema instance to be defined in global scope called "Schema", in way similar to one in generated code.

3. Web service
--------------

When WSDL file is provided server or client code can be generated using wsdl2py script. If not, advised would be to write code first a then use browser to request specification. Accessing URL <your webservice context>?wsdl with browser will give current WSDL with XSD embaded. 

3.1 Generating code from WSDL file
''''''''''''''''''''''''''''''''''

*wsdl2py* can generate either client or server code. For server use -s, client -c flag. Server example: {{{wsdl2py.py -s Specifications\ops.wsdl}}}

.. code-block:: python

    # ...XSD part truncated...
    PutOps_method = xsd.Method(function = PutOps,
        soapAction = "http://polaris.flightdataservices.com/ws/ops/PutOps",
        input = "ops",#Pointer to Schema.elements
        output = "status",#Pointer to Schema.elements
        operationName = "PutOps")

    SERVICE = soap.Service(
        targetNamespace = "http://flightdataservices.com/ops.wsdl",
        location = "http://polaris.flightdataservices.com/ws/ops",
        schema = Schema,
        methods = [PutOps_method, ])


Generated code includes: methods descriptions, service description, dispatcher and Django ulrs.py binding.

xsd.Method describes one method for service(that can consist from more then one method). Methods give dispatcher informations required for method distinction - soapAction and operationName, and function to call on incoming SOAP message. 
For detail field meaning see xsd.Method pydoc.

SERVICE aggregates all informations required for WSDL generation and correct dispatching. get_django_dispatch returns a function binded to SERVICE that pointed from urls.py will call appropriate function on incoming SOAP message. The called function, in this example PutOps, is expected to return object from XSD that could be translated 
to correct and valid response - for this example this would be Status instance.  

URLs binding it is commented out, paste this code into your urls.py and change <fill the module path> to point file where to code was generated.

3.2 Client
''''''''''

Client can be generated with flag -c: {{{wsdl2py.py -c examples\ops.wsdl}}}

Generated code:

.. code-block:: python

    # ...XSD Part truncated ...
    PutOps_method = xsd.Method(
       soapAction = "http://polaris.flightdataservices.com/ws/ops/PutOps",
       input = "ops",#Pointer to Schema.elements
       output = "status",#Pointer to Schema.elements
       operationName = "PutOps")

    SERVICE = soap.Service(
        targetNamespace = "http://flightdataservices.com/ops.wsdl",
        location = "http://polaris.flightdataservices.com/ws/ops",
        schema = Schema,
        methods = [PutOps_method, ])


    class ServiceStub(soap.Stub):
        SERVICE = SERVICE

        def PutOps(self, ops):
            return self.call("PutOps", ops)


ServiceStub is a proxy object that defines methods available on remote webservice. Calling one of those method, in the example there is only one PutOps, will produce SOAP call to remote server defined in SERVICE. The methods will return appropriate object from XSD description or raise an exception on any problems.

For more real example: See examples\client.py 

3.3. Building Webservice
''''''''''''''''''''''''

The build a webservice we need to define few things: 
 * Classes that would be send via SOAP
 * Schema instance that aggregates all classes with name space etc., 
 * Web service functions and all related informations
 * Service instance to put everything together 
 * Binding to URL

Lets build the stock web service that will give a stock price for 
provided company code and datetime.

3.3.1 Stack classes
...................

.. code-block:: python

    class GetStockPrice(xsd.ComplexType):
        company = xsd.Element(xsd.String, minOccurs=1)
        datetime = xsd.Element(xsd.DateTime)

    class StockPrice(xsd.ComplexType):
        price = xsd.Element(xsd.Integer)

    Schema = xsd.Schema(
          #Should be unique URL, can be any string.
          targetNamespace = "http://code.google.com/p/soapfish/stock.xsd",
          #Register all complex types to schema.
          complexTypes = [GetStockPrice, StockPrice],
          elements = {"getStockPrice":xsd.Element(GetStockPrice), 
                      "stockPrice":xsd.Element(StockPrice)}              
    )


Note the elements in schema, for this version it is required to create 
an element of specific type and use it string element name as input/output in Service definitions. WSDL specifications allows also direct use of type, which is not covered yet.

3.3.2 Metod definition
......................

.. code-block:: python

    def get_stock_price(request, gsp):
        print gsp.company
        return StockPrice(price=139)

    get_stock_price_method = xsd.Method(
        function = get_stock_price,
        soapAction = "http://code.google.com/p/soapfish/stock/get_stock_price",
        input = "getStockPrice",
        output = "stockPrice",
        operationName = "GetStockPrice")


3.3.3 Puting all together
.........................

.. code-block:: python

    SERVICE = soap.Service(
        #WSDL targetNamespce
        targetNamespace = "http://code.google.com/p/soapfish/stock.wsdl",
        #The url were request should be send.
        location = "http://127.0.0.1:8000/stock",
        schema = Schema,
        methods = [get_stock_price_method])


and wsgi.py

.. code-block:: python

    from wsgiref.simple_server import make_server
    from soapfish import soap_dispatch
    from service_gen import SERVICE

    dispatcher = soap_dispatch.SOAPDispatcher(SERVICE)
    app = soap_dispatch.WsgiSoapApplication({'/ChargePoint/services/chargePointService': dispatcher})

    httpd = make_server('', 8000, app)
    print("Serving HTTP on port 8000...")
    httpd.serve_forever()


Now requesting http://127.0.0.1:8000/stock?wsdl will give service specification and SOAP messages like:

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

 
