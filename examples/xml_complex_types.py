# Example 3. Nested ComplexTypes with attributes.

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


flight = Flight(tail_number='G-DEMO')  # Constructor handles field inititailization.
flight.takeoff_airport = Airport(type='IATA', code='WAW')
flight.landing_airport = Airport(type='ICAO', code='EGLL')

print(flight.xml('flight'))
# datetime field types will accept, datetime object or string, that parses correctly to such object.
flight.takeoff_datetime = datetime.now()
print(flight.xml('flight'))
