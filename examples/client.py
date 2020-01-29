from soapfish import soap, xsd


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
    takeoff_airport = xsd.Element('Airport')
    takeoff_gate_datetime = xsd.Element(xsd.DateTime, minOccurs=0)
    takeoff_datetime = xsd.Element(xsd.DateTime)
    takeoff_fuel = xsd.Element('Weight', minOccurs=0)
    takeoff_gross_weight = xsd.Element('Weight', minOccurs=0)
    takeoff_pilot = xsd.Element('Pilot', minOccurs=0)
    landing_airport = xsd.Element('Airport')
    landing_gate_datetime = xsd.Element(xsd.DateTime, minOccurs=0)
    landing_datetime = xsd.Element(xsd.DateTime)
    landing_fuel = xsd.Element('Weight', minOccurs=0)
    landing_pilot = xsd.Element('Pilot', minOccurs=0)
    destination_airport = xsd.Element('Airport', minOccurs=0)
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
    elements={'ops': xsd.Element('Ops'), 'status': xsd.Element('Status')})


PutOps_method = xsd.Method(
    soapAction='http://polaris.flightdataservices.com/ws/ops/PutOps',
    input='ops',  # Pointer to Schema.elements
    inputPartName='body',
    output='status',  # Pointer to Schema.elements
    outputPartName='body',
    operationName='PutOps')


PutOpsPort_SERVICE = soap.Service(
    name='PutOpsPort',
    targetNamespace='http://flightdataservices.com/ops.wsdl',
    location='http://127.0.0.1:8088/mockPutOpsBinding',
    schema=Schema,
    version=soap.SOAPVersion.SOAP11,
    methods=[PutOps_method])


class PutOpsPortServiceStub(soap.Stub):
    SERVICE = PutOpsPort_SERVICE

    def PutOps(self, ops):  # noqa
        return self.call('PutOps', ops)


if __name__ == '__main__':
    from datetime import datetime
    stub = PutOpsPortServiceStub()
    ops = Ops()
    ops.aircraft = 'LN-KKU'
    ops.flight_number = '1234'
    ops.type = 'COMMERCIAL'
    ops.takeoff_airport = Airport.create(code_type='IATA', code='WAW')
    ops.takeoff_datetime = datetime.now()
    ops.landing_airport = Airport.create(code_type='ICAO', code='EGLL')
    ops.landing_datetime = datetime.now()
    status = stub.PutOps(ops)
    print((status.action, status.id))
