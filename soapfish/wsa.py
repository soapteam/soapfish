import os
import uuid

from lxml import etree

from . import namespaces as ns, xsd

NAMESPACE = ns.wsa
ANONYMOUS = 'http://www.w3.org/2005/08/addressing/anonymous'
SCHEMA_IMPORT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'raw', 'wsa.xsd'))


class ReplyTo(xsd.ComplexType):
    Address = xsd.Element(xsd.String, tagname='Address', namespace=ns.wsa)


class Header(xsd.ComplexType):
    Action = xsd.Element(xsd.String, tagname='Action', namespace=ns.wsa)
    MessageID = xsd.Element(xsd.String, tagname='MessageID', namespace=ns.wsa)
    To = xsd.Element(xsd.String, tagname='To', namespace=ns.wsa)
    ReplyTo = xsd.Element(ReplyTo, tagname='ReplyTo', namespace=ns.wsa, minOccurs=0)
    RelatesTo = xsd.Element(xsd.String, namespace=ns.wsa, minOccurs=0)


SCHEMA = xsd.Schema(
    targetNamespace=ns.wsa,
    elementFormDefault=xsd.ElementFormDefault.QUALIFIED,
    simpleTypes=[],
    attributeGroups=[],
    groups=[],
    complexTypes=[ReplyTo, Header],
    elements={},
)
XSD_SCHEMA = etree.parse(SCHEMA_IMPORT_PATH)
XML_SCHEMA = etree.XMLSchema(XSD_SCHEMA)


def fill_header(dst_header, src_header=None):
    """Fill dst_header with the basic information based on src_header."""
    if src_header:
        dst_header.Action = src_header.Action + 'Response'
        dst_header.RelatesTo = src_header.MessageID
    dst_header.MessageID = str(uuid.uuid1())
    dst_header.To = ANONYMOUS
