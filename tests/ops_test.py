import unittest

import iso8601
from lxml import etree

from soapfish import py2xsd, xsd


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
        'COMMERCIAL', 'INCOMPLETE', 'ENGINE_RUN_UP', 'TEST', 'TRAINING', 'FERRY', 'POSITIONING', 'LINE_TRAINING',
    ]))
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
    simpleTypes=[Pilot],
    attributeGroups=[],
    groups=[],
    complexTypes=[Airport, Weight, Ops, Status],
    elements={'ops': xsd.Element(Ops), 'status': xsd.Element(Status)})


XML_REQUIRED_ONLY = '''
<ops:ops xmlns:ops="http://flightdataservices.com/ops.xsd">
    <aircraft>N608WB</aircraft>
    <flight_number>123123</flight_number>
    <type>COMMERCIAL</type>

    <takeoff_airport>
        <code_type>ICAO</code_type>
        <code>EGLL</code>
    </takeoff_airport>

    <takeoff_gate_datetime>2009-12-30T21:35:59</takeoff_gate_datetime>
    <takeoff_datetime>2009-12-30T21:39:59</takeoff_datetime>
    <landing_airport>
        <code_type>ICAO</code_type>
        <code>EPWA</code>
    </landing_airport>

    <landing_gate_datetime>2009-12-30T23:35:59</landing_gate_datetime>
    <landing_datetime>2009-12-30T23:32:59</landing_datetime>
</ops:ops>'''


class OPS_Test(unittest.TestCase):
    def test_required_only(self):
        XMLSchema = etree.XMLSchema(py2xsd.generate_xsd(Schema))
        ops = Ops.parsexml(XML_REQUIRED_ONLY, XMLSchema)
        self.assertEqual('N608WB', ops.aircraft)
        self.assertEqual('123123', ops.flight_number)
        self.assertEqual('COMMERCIAL', ops.type)
        self.assertEqual('ICAO', ops.takeoff_airport.code_type)
        self.assertEqual('EGLL', ops.takeoff_airport.code)
        self.assertIsNone(ops.takeoff_pilot)
        self.assertEqual(iso8601.parse_date('2009-12-30T23:35:59Z'), ops.landing_gate_datetime)
