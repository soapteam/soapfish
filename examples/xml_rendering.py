#Example 1. Rendering object to XML.

from __future__ import print_function

from soapbox import xsd


class Airport(xsd.ComplexType):
    type = xsd.Element(xsd.String)
    code = xsd.Element(xsd.String)


airport = Airport()
airport.type = "IATA"
airport.code = "WAW"
print(airport.xml("takeoff_airport"))
