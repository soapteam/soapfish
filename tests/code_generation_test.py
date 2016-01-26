import os
import unittest
import tempfile

from lxml import etree
import six
from pythonic_testcase import *

from soapfish.xsd2py import generate_code_from_xsd
from soapfish.wsdl2py import generate_code_from_wsdl
from soapfish import py2wsdl
from soapfish.utils import open_document


XSD = """
<xsd:schema xmlns:sns="http://flightdataservices.com/ops.xsd"
xmlns:xsd="http://www.w3.org/2001/XMLSchema"
targetNamespace="http://flightdataservices.com/ops.xsd"
xmlns="http://flightdataservices.com/ops.xsd">
  <xsd:simpleType name="pilot">
    <xsd:restriction base="xsd:string">
      <xsd:enumeration value="CAPTAIN"/>
      <xsd:enumeration value="FIRST_OFFICER"/>
    </xsd:restriction>
  </xsd:simpleType>
  <xsd:complexType name="airport">
    <xsd:sequence>
      <xsd:element name="code_type">
        <xsd:simpleType>
          <xsd:restriction base="xsd:string">
            <xsd:enumeration value="ICAO"/>
            <xsd:enumeration value="IATA"/>
            <xsd:enumeration value="FAA"/>
          </xsd:restriction>
        </xsd:simpleType>
      </xsd:element>
      <xsd:element name="code" type="xsd:string"/>
    </xsd:sequence>
  </xsd:complexType>
  <xsd:complexType name="weight">
    <xsd:sequence>
      <xsd:element name="value" type="xsd:integer"/>
      <xsd:element name="unit">
        <xsd:simpleType>
          <xsd:restriction base="xsd:string">
            <xsd:enumeration value="kg"/>
            <xsd:enumeration value="lb"/>
          </xsd:restriction>
        </xsd:simpleType>
      </xsd:element>
    </xsd:sequence>
  </xsd:complexType>
  <xsd:complexType name="ops">
    <xsd:sequence>
      <xsd:element name="aircraft" type="xsd:string"/>
      <xsd:element name="flight_number" type="xsd:string"/>
      <xsd:element name="type">
        <xsd:simpleType>
          <xsd:restriction base="xsd:string">
            <xsd:enumeration value="COMMERCIAL"/>
            <xsd:enumeration value="INCOMPLETE"/>
            <xsd:enumeration value="ENGINE_RUN_UP"/>
            <xsd:enumeration value="TEST"/>
            <xsd:enumeration value="TRAINING"/>
            <xsd:enumeration value="FERRY"/>
            <xsd:enumeration value="POSITIONING"/>
            <xsd:enumeration value="LINE_TRAINING"/>
          </xsd:restriction>
        </xsd:simpleType>
      </xsd:element>
      <xsd:element name="takeoff_airport" type="sns:airport"/>
      <xsd:element name="takeoff_gate_datetime" type="xsd:dateTime" minOccurs="0"/>
      <xsd:element name="takeoff_datetime" type="xsd:dateTime"/>
      <xsd:element name="takeoff_fuel" type="sns:weight" minOccurs="0"/>
      <xsd:element name="takeoff_gross_weight" type="sns:weight" minOccurs="0"/>
      <xsd:element name="takeoff_pilot" type="sns:pilot" minOccurs="0"/>
      <xsd:element name="landing_airport" type="sns:airport"/>
      <xsd:element name="landing_gate_datetime" type="xsd:dateTime" minOccurs="0"/>
      <xsd:element name="landing_datetime" type="xsd:dateTime"/>
      <xsd:element name="landing_fuel" type="sns:weight" minOccurs="0"/>
      <xsd:element name="landing_pilot" type="sns:pilot" minOccurs="0"/>
      <xsd:element name="destination_airport" type="sns:airport" minOccurs="0"/>
      <xsd:element name="captain_code" type="xsd:string" minOccurs="0"/>
      <xsd:element name="first_officer_code" type="xsd:string" minOccurs="0"/>
      <xsd:element name="V2" type="xsd:integer" minOccurs="0"/>
      <xsd:element name="Vref" type="xsd:integer" minOccurs="0"/>
      <xsd:element name="Vapp" type="xsd:integer" minOccurs="0"/>
    </xsd:sequence>
  </xsd:complexType>
  <xsd:complexType name="status">
    <xsd:sequence>
      <xsd:element name="action">
        <xsd:simpleType>
          <xsd:restriction base="xsd:string">
            <xsd:enumeration value="INSERTED"/>
            <xsd:enumeration value="UPDATED"/>
            <xsd:enumeration value="EXISTS"/>
          </xsd:restriction>
        </xsd:simpleType>
      </xsd:element>
      <xsd:element name="id" type="xsd:long"/>
    </xsd:sequence>
  </xsd:complexType>
  <xsd:element name="status" type="sns:status"/>
  <xsd:element name="ops" type="sns:ops"/>
</xsd:schema>
"""

XSD_RESTRICTION = b"""<?xml version="1.0" encoding="UTF-8"?>
<xsd:schema elementFormDefault="qualified" targetNamespace="http://example.com" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <xsd:complexType name="ComplexType">
        <xsd:sequence>
            <xsd:element name="RestrictedString">
                <xsd:simpleType>
                    <xsd:restriction base="xsd:string">
                        <xsd:maxLength value="60" />
                    </xsd:restriction>
                </xsd:simpleType>
            </xsd:element>
        </xsd:sequence>
    </xsd:complexType>
</xsd:schema>
"""

XSD_LIST_PARAM = b"""<xsd:schema xmlns:sns="http://flightdataservices.com/ops.xsd"
xmlns:xsd="http://www.w3.org/2001/XMLSchema"
targetNamespace="http://flightdataservices.com/ops.xsd"
xmlns="http://flightdataservices.com/ops.xsd">
  <xsd:complexType name="airport">
    <xsd:sequence>
      <xsd:element name="Items" type="xsd:String" minOccurs="1" maxOccurs="unbounded"></xsd:element>
    </xsd:sequence>
  </xsd:complexType>
</xsd:schema>
"""

WSDL = b"""<?xml version="1.0" encoding="utf-8"?>
<wsdl:definitions xmlns:tns="http://flightdataservices.com/ops.wsdl" xmlns:xs="http://www.w3.org/2000/10/XMLSchema" xmlns:fds="http://flightdataservices.com/ops.xsd" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" name="OPS" targetNamespace="http://flightdataservices.com/ops.wsdl" xmlns="http://flightdataservices.com/ops.xsd">
    <wsdl:types>
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" targetNamespace="http://flightdataservices.com/ops.xsd">
            <xs:complexType name="airport">
                <xs:sequence>
                    <xs:element name="code_type">
                        <xs:simpleType>
                            <xs:restriction base="xs:string">
                                <xs:enumeration value="ICAO"/>
                                <xs:enumeration value="IATA"/>
                                <xs:enumeration value="FAA"/>
                            </xs:restriction>
                        </xs:simpleType>
                    </xs:element>
                    <xs:element name="code" type="xs:string"/>
                </xs:sequence>
            </xs:complexType>

            <xs:complexType name="weight">
                    <xs:sequence>
                        <xs:element name="value" type="xs:integer"/>
                        <xs:element name="unit">
                            <xs:simpleType>
                                <xs:restriction base="xs:string">
                                    <xs:enumeration value="kg"/>
                                    <xs:enumeration value="lb"/>
                                </xs:restriction>
                        </xs:simpleType>
                        </xs:element>
                    </xs:sequence>
            </xs:complexType>

            <xs:simpleType name="pilot">
                <xs:restriction base="xs:string">
                    <xs:enumeration value="CAPTAIN"/>
                    <xs:enumeration value="FIRST_OFFICER"/>
                </xs:restriction>
            </xs:simpleType>

            <xs:complexType name="ops">
                <xs:sequence>
                    <xs:element name="aircraft" type="xs:string" nillable="false"/>
                    <xs:element name="flight_number" type="xs:string"/>
                    <xs:element name="type">
                        <xs:simpleType>
                            <xs:restriction base="xs:string">
                                <xs:enumeration value="COMMERCIAL"/>
                                <xs:enumeration value="INCOMPLETE"/>
                                <xs:enumeration value="ENGINE_RUN_UP"/>
                                <xs:enumeration value="TEST"/>
                                <xs:enumeration value="TRAINING"/>
                                <xs:enumeration value="FERRY"/>
                                <xs:enumeration value="POSITIONING"/>
                                <xs:enumeration value="LINE_TRAINING"/>
                            </xs:restriction>
                        </xs:simpleType>
                    </xs:element>
                    <xs:element name="takeoff_airport" type="fds:airport"/>
                    <xs:element name="takeoff_gate_datetime" type="xs:dateTime" minOccurs="0"/>
                    <xs:element name="takeoff_datetime" type="xs:dateTime"/>
                    <xs:element name="takeoff_fuel" minOccurs="0" type="fds:weight"/>
                    <xs:element name="takeoff_gross_weight" minOccurs="0" type="fds:weight"/>
                    <xs:element name="takeoff_pilot" minOccurs="0" type="fds:pilot"/>
                    <xs:element name="landing_airport" type="fds:airport"/>
                    <xs:element name="landing_gate_datetime" type="xs:dateTime" minOccurs="0"/>
                    <xs:element name="landing_datetime" type="xs:dateTime"/>
                    <xs:element name="landing_fuel" minOccurs="0" type="fds:weight"/>
                    <xs:element name="landing_pilot" minOccurs="0" type="fds:pilot"/>
                    <xs:element name="destination_airport" minOccurs="0" type="fds:airport"/>
                    <xs:element name="captain_code" minOccurs="0" type="xs:string"/>
                    <xs:element name="first_officer_code" minOccurs="0" type="xs:string"/>
                    <xs:element name="V2" minOccurs="0" type="xs:integer"/>
                    <xs:element name="Vref" minOccurs="0" type="xs:integer"/>
                    <xs:element name="Vapp" minOccurs="0" type="xs:integer"/>
                </xs:sequence>
            </xs:complexType>
            <xs:complexType name="status">
                <xs:sequence>
                    <xs:element name="action">
                        <xs:simpleType>
                            <xs:restriction base="xs:string">
                                <xs:enumeration value="INSERTED"/>
                                <xs:enumeration value="UPDATED"/>
                                <xs:enumeration value="EXISTS"/>
                            </xs:restriction>
                        </xs:simpleType>
                    </xs:element>
                    <xs:element name="id" type="xs:long"/>
                </xs:sequence>
            </xs:complexType>
            <xs:element name="ops" type="fds:ops"/>
            <xs:element name="status" type="fds:status"/>
        </xs:schema>
    </wsdl:types>
    <wsdl:message name="PutOpsInput">
        <wsdl:part name="body" element="fds:ops"/>
    </wsdl:message>
    <wsdl:message name="PutOpsOutput">
        <wsdl:part name="body" element="fds:status"/>
    </wsdl:message>
    <wsdl:portType name="PutOpsPortType">
        <wsdl:operation name="PutOps">
            <wsdl:input message="tns:PutOpsInput"/>
            <wsdl:output message="tns:PutOpsOutput"/>
        </wsdl:operation>
    </wsdl:portType>
    <wsdl:binding name="PutOpsBinding" type="tns:PutOpsPortType">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <wsdl:operation name="PutOps">
            <soap:operation soapAction="http://polaris.flightdataservices.com/ws/ops/PutOps"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>
    </wsdl:binding>
    <wsdl:service name="OPS">
        <wsdl:documentation>Register Flight Ops</wsdl:documentation>
        <wsdl:port name="PutOpsPort" binding="tns:PutOpsBinding">
            <soap:address location="http://polaris.flightdataservices.com/ws/ops"/>
        </wsdl:port>
    </wsdl:service>
</wsdl:definitions>"""


class CodeGenerationTest(unittest.TestCase):

    def test_code_generation_from_xsd(self):
        xmlelement = etree.fromstring(XSD)
        # Add mandatory imports to test the generated code
        code = b'from soapfish import soap, xsd\n' + generate_code_from_xsd(xmlelement)
        self._exec(code, {})

    def test_code_generation_from_wsdl_client(self):
        code = generate_code_from_wsdl(WSDL, 'client')
        m = {}
        self._exec(code, m)
        self.check_reparse_wsdl(m, 'client')

    def test_code_generation_from_wsdl_server(self):
        code = generate_code_from_wsdl(WSDL, 'server')
        m = {}
        self._exec(code, m)
        self.check_reparse_wsdl(m, 'server')

    def _exec(self, code, globalz):
        _, fname = tempfile.mkstemp(suffix='.py')
        file_header = ('# -*- coding: utf-8 -*-\n'
            'import sys\n'
            'import os\n'
            'sys.path.append(os.path.dirname("{0}"))\n').format(fname).encode('utf8')
        code = file_header + b'\n' + code + b'\n'
        #print(code.decode('utf8'))
        with open(fname, 'wb') as f:
            # Empty last line is mandatory for python2.6
            f.write(code)
        compiled_code = compile(code, fname, 'exec')
        globalz['__name__'] = fname.rsplit('/', 1)[-1].rsplit('.', 1)[0]
        exec(code, globalz)

    def check_reparse_wsdl(self, base, target):
        xml = py2wsdl.tostring(base['PutOpsPort_SERVICE'])
        code = generate_code_from_wsdl(xml, target)
        m = {}
        self._exec(code, m)
        # XXX too much autonaming magic
        m['PutOpsPort_SERVICE'] = m.pop('PutOpsPortPort_SERVICE')
        if target == 'client':
            m['PutOpsPortServiceStub'] = m.pop('PutOpsPortPortServiceStub')
        assert_equals(sorted(m), sorted(base))

    def test_relative_paths(self):
        path = 'tests/assets/relative/relative.wsdl'
        xml = open_document(path)
        code = generate_code_from_wsdl(xml, 'server', cwd=os.path.dirname(path))
        if six.PY3:
            code = code.decode()
        assert_contains('Schema2_Element', code)
        assert_contains('Schema3_Element', code)
        assert_equals(1, code.count('Schema3_Element'))

    def test_import_same_namespace(self):
        path = 'tests/assets/same_namespace/same_namespace.wsdl'
        xml = open_document(path)
        code = generate_code_from_wsdl(xml, 'server', cwd=os.path.dirname(path))
        if six.PY3:
            code = code.decode()
        assert_contains('Schema1_Element', code)
        assert_contains('Schema2_Element', code)

    def test_schema_xsd_include(self):
        path = 'tests/assets/include/include.wsdl'
        xml = open_document(path)
        code = generate_code_from_wsdl(xml, 'server', cwd=os.path.dirname(path))
        if six.PY3:
            code = code.decode()
        assert_contains('Schema1_Element', code)

    def test_schema_xsd_restriction(self):
        xmlelement = etree.fromstring(XSD_RESTRICTION)
        code = generate_code_from_xsd(xmlelement)
        if six.PY3:
            code = code.decode()
        compile(code, 'restriction', 'exec')

    def test_create_method_list_param(self):
        xmlelement = etree.fromstring(XSD_LIST_PARAM)
        code = generate_code_from_xsd(xmlelement)
        if six.PY3:
            code = code.decode()
        assert_contains("def create(cls, Items):", code)
        assert_contains("instance.Items = Items", code)
        assert_not_contains("Itemss", code)

if __name__ == "__main__":
    unittest.main()
