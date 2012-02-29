from optparse import OptionParser
from lxml import etree
from jinja2 import Environment, PackageLoader
from wsdl import get_wsdl_classes, get_by_name
from utils import removens, classyfiy, get_get_type, use, find_xsd_namepsace, urlcontext
from xsd2py import schema_to_py, schema_name, open_document
from soap import SOAP_HTTP_Transport, SOAPVersion


environment = Environment(
    extensions=['jinja2.ext.loopcontrols'],
    loader=PackageLoader(*'soapbox.templates'.split('.')),
)
environment.filters["class"] = classyfiy
environment.filters["removens"] = removens
environment.filters["use"] = use
environment.filters["urlcontext"] = urlcontext
environment.globals["get_by_name"] = get_by_name
environment.globals["SOAPTransport"] = SOAP_HTTP_Transport
environment.globals["schema_name"] = schema_name


def generate_code_from_wsdl(is_server, xml):
    xmlelement = etree.fromstring(xml)
    XSD_NAMESPACE = find_xsd_namepsace(xmlelement.nsmap)
    environment.filters["type"] = get_get_type(XSD_NAMESPACE)

    wsdl = get_wsdl_classes(SOAPVersion.SOAP11.BINDING_NAMESPACE)
    definitions = wsdl.Definitions.parse_xmlelement(xmlelement)
    schema = definitions.types.schema
    xsd_namespace = find_xsd_namepsace(xmlelement.nsmap)
    schemaxml = schema_to_py(schema, xsd_namespace)
    return environment.get_template('wsdl').render(
            definitions=definitions,
            schema=schemaxml,
            is_server=is_server)


def console_main():
    parser = OptionParser(usage="usage: %prog [-c|-s] path_to_wsdl")
    parser.add_option("-c", "--client", dest="client",
                  help="Generate webservice http client code.")
    parser.add_option("-s", "--server", dest="server",
                  help="Generate webservice Django server code.")
    (options, args) = parser.parse_args()
    if options.client and options.server:
        parser.error("Options -c and -s are mutually exclusive")
    elif options.client:
        xml = open_document(options.client)
        print generate_code_from_wsdl(False, xml)
    elif options.server:
        xml = open_document(options.server)
        print generate_code_from_wsdl(True, xml)
    else:
        parser.print_help()


if __name__ == "__main__":
    console_main()
    #url = "http://ec2-46-137-40-70.eu-west-1.compute.amazonaws.com/QPulse5WebServices/Services/Core.svc?wsdl"
    #resolve_imports(url)
