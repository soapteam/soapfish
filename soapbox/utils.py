import xsd
from urlparse import urlparse


def removens(full_typename):
    if full_typename is None:
        return None
    return full_typename.split(':')[-1]


def classyfiy(value):
    return value[0].upper() + value[1:]


def get_get_type(XSD_NAMESPACES):
    def get_type(full_typename):
        if full_typename is None:
            return None

        typename = full_typename.split(":")
        if len(typename) == 2:
            ns, typename = typename
        else:
            ns = None
            typename = typename[0]
        if ns in XSD_NAMESPACES:
            return "xsd." + classyfiy(typename)
        else:
            return '"%s"' % classyfiy(typename)
    return get_type


def use(usevalue):
    if usevalue == xsd.Use.OPTIONAL:
        return "xsd.Use.OPTIONAL"
    elif usevalue == xsd.Use.REQUIRED:
        return "xsd.Use.REQUIRED"
    elif usevalue == xsd.Use.PROHIBITED:
        return "xsd.Use.PROHIBITED"
    else:
        raise ValueError


def find_xsd_namepsace(nsmap):
    namespaces = []
    for key, value in nsmap.iteritems():
        if value == "http://www.w3.org/2001/XMLSchema"\
        or value == "http://www.w3.org/2000/10/XMLSchema":
            namespaces.append(key)
    return namespaces


def urlcontext(url):
    """http://polaris.flightdataservices.com/ws/ops-> ^ws/ops$"""
    o = urlparse(url)
    path = o.path.lstrip('/')
    return r'^%s$' % path  # build regex


def uncapitalize(value):
    if value == "QName":
        return value
    else:
        return value[0].lower() + value[1:]
