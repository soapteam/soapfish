from soapfish import soap, xsd


class GetStockPrice(xsd.ComplexType):
    company = xsd.Element(xsd.String, minOccurs=1)
    datetime = xsd.Element(xsd.DateTime)


class StockPrice(xsd.ComplexType):
    nillable = xsd.Element(xsd.Int, nillable=True)
    prices = xsd.ListElement(xsd.Decimal(fractionDigits=2), tagname='price', minOccurs=0, maxOccurs=xsd.UNBOUNDED, nillable=True)


Schema = xsd.Schema(
    # Should be unique URL, can be any string.
    targetNamespace='http://code.google.com/p/soapfish/stock.xsd',
    # Register all complex types to schema.
    complexTypes=[GetStockPrice, StockPrice],
    elements={'getStockPrice': xsd.Element(GetStockPrice), 'stockPrice': xsd.Element(StockPrice)},
)


def get_stock_price(request, gsp):
    print((gsp.company, gsp.datetime))
    sp = StockPrice(nillable=xsd.NIL)
    sp.prices.append(13.29)
    sp.prices.append(4.56)
    sp.prices.append(xsd.NIL)
    return sp


get_stock_price_method = xsd.Method(
    function=get_stock_price,
    soapAction='http://code.google.com/p/soapfish/stock/get_stock_price',
    input='getStockPrice',
    output='stockPrice',
    operationName='GetStockPrice')


SERVICE11 = soap.Service(
    name='StockService',
    targetNamespace='http://code.google.com/p/soapfish/stock.wsdl',  # WSDL targetNamespce
    version=soap.SOAPVersion.SOAP11,
    # The url were request should be send.
    location='http://127.0.0.1:8000/stock/soap11',
    schema=Schema,
    methods=[get_stock_price_method])


SERVICE12 = soap.Service(
    # WSDL targetNamespce
    name='StockService',
    targetNamespace='http://code.google.com/p/soapfish/stock.wsdl',
    version=soap.SOAPVersion.SOAP12,
    # The url where request should be sent.
    location='http://127.0.0.1:8000/stock/soap12',
    schema=Schema,
    methods=[get_stock_price_method])


# ------------------------------------------------------------------------------


class Pilot(xsd.String):
    enumeration = ['CAPTAIN', 'FIRST_OFFICER']


class Airport(xsd.ComplexType):
    INHERITANCE = None
    INDICATOR = xsd.Sequence
    code_type = xsd.Element(xsd.String(enumeration=['ICAO', 'IATA', 'FAA']))
    code = xsd.Element(xsd.String)

    @classmethod
    def create(cls, code_type, code):
        instance = cls()
        instance.code_type = code_type
        instance.code = code
        return instance


class Weight(xsd.ComplexType):
    INHERITANCE = None
    INDICATOR = xsd.Sequence
    value = xsd.Element(xsd.Integer)
    unit = xsd.Element(xsd.String(enumeration=['kg', 'lb']))

    @classmethod
    def create(cls, value, unit):
        instance = cls()
        instance.value = value
        instance.unit = unit
        return instance


class Ops(xsd.ComplexType):
    INHERITANCE = None
    INDICATOR = xsd.Sequence
    aircraft = xsd.Element(xsd.String)
    flight_number = xsd.Element(xsd.String)
    type = xsd.Element(xsd.String(
        enumeration=['COMMERCIAL', 'INCOMPLETE', 'ENGINE_RUN_UP', 'TEST', 'TRAINING', 'FERRY', 'POSITIONING', 'LINE_TRAINING'],
    ))
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

    @classmethod
    def create(cls, aircraft, flight_number, type, takeoff_airport, takeoff_datetime, landing_airport, landing_datetime):
        instance = cls()
        instance.aircraft = aircraft
        instance.flight_number = flight_number
        instance.type = type
        instance.takeoff_airport = takeoff_airport
        instance.takeoff_datetime = takeoff_datetime
        instance.landing_airport = landing_airport
        instance.landing_datetime = landing_datetime
        return instance


class Status(xsd.ComplexType):
    INHERITANCE = None
    INDICATOR = xsd.Sequence
    action = xsd.Element(xsd.String(enumeration=['INSERTED', 'UPDATED', 'EXISTS']))
    id = xsd.Element(xsd.Long)

    @classmethod
    def create(cls, action, id):
        instance = cls()
        instance.action = action
        instance.id = id
        return instance


Schema = xsd.Schema(
    targetNamespace='http://flightdataservices.com/ops.xsd',
    elementFormDefault='unqualified',
    simpleTypes=[Pilot],
    attributeGroups=[],
    groups=[],
    complexTypes=[Airport, Weight, Ops, Status],
    elements={'ops': xsd.Element(Ops), 'status': xsd.Element(Status)})


def PutOps(request, ops):  # noqa
    print((ops.aircraft, ops.takeoff_datetime))
    return Status(id=100, action='INSERTED')


PutOps_method = xsd.Method(
    function=PutOps,
    soapAction='http://polaris.flightdataservices.com/ws/ops/PutOps',
    input='ops',  # Pointer to Schema.elements
    output='status',  # Pointer to Schema.elements
    operationName='PutOps')


SERVICE = soap.Service(
    targetNamespace='http://flightdataservices.com/ops.wsdl',
    location='http://polaris.flightdataservices.com/ws/ops',
    schema=Schema,
    methods=[PutOps_method])
