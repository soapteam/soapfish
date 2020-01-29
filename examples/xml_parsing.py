# Example 2. Parsing XML to object.

from soapfish import xsd


class Airport(xsd.ComplexType):
    type = xsd.Element(xsd.String)
    code = xsd.Element(xsd.String)


XML = '''<takeoff_airport>
  <type>IATA</type>
  <code>WAW</code>
</takeoff_airport>'''


airport = Airport.parsexml(XML)
print('Type:', airport.type)
print('Code:', airport.code)
