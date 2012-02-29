from lxml import etree
import keyword
import sys
import httplib2
import hashlib
from jinja2 import Environment, PackageLoader
from xsdspec import Schema
from utils import removens, classyfiy, get_get_type, use, find_xsd_namepsace


def schema_name(namespace):
    return hashlib.sha512(namespace).hexdigest()[0:5]


def generate_code_from_xsd(xmlelement, known_namespaces=None, location=None):
    if known_namespaces is None:
        known_namespaces = []
    XSD_NAMESPACE = find_xsd_namepsace(xmlelement.nsmap)

    schema = Schema.parse_xmlelement(xmlelement)
    if schema.targetNamespace in known_namespaces:
        return ""
    else:
        return schema_to_py(schema, XSD_NAMESPACE, known_namespaces, location)


def schema_to_py(schema, xsd_namespce, known_namespaces=None, location=None):
    if known_namespaces is None:
        known_namespaces = []
    known_namespaces.append(schema.targetNamespace)

    environment = Environment(
        extensions=['jinja2.ext.loopcontrols'],
        loader=PackageLoader(*'soapbox.templates'.split('.')),
    )
    environment.filters["class"] = classyfiy
    environment.filters["removens"] = removens
    environment.filters["use"] = use
    environment.filters["type"] = get_get_type(xsd_namespce)
    environment.globals["resolve_import"] = resolve_import
    environment.globals["known_namespaces"] = known_namespaces
    environment.globals["schema_name"] = schema_name
    environment.globals["location"] = location
    environment.globals["keywords"] = keyword.kwlist
    return environment.get_template('xsd').render(schema=schema)


def resolve_import(xsdimport, known_namespaces):
    xml = open_document(xsdimport.schemaLocation)
    xmlelement = etree.fromstring(xml)
    return generate_code_from_xsd(xmlelement, known_namespaces, xsdimport.schemaLocation)


def open_document(document_address):
    if document_address.startswith("http:"):
        http = httplib2.Http()
        _, content = http.request(document_address)
        return content
    else:
        return open(document_address).read()


def main():
    if len(sys.argv) != 2:
        print "use: xsd2py <path to xsd>"
        return
    xml = open(sys.argv[1]).read()
    xmlelement = etree.fromstring(xml)
    print """from soapbox import xsd
from soapbox.xsd import UNBOUNDED"""
    print generate_code_from_xsd(xmlelement)

if __name__ == "__main__":
    main()
