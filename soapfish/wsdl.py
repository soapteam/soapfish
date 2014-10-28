# -*- coding: utf-8 -*-

from . import namespaces as ns


# --- Functions ---------------------------------------------------------------
def get_by_name(_list, fullname):
    name = fullname.split(':')[-1]
    for item in _list:
        if item.name == name:
            return item
    raise ValueError("Item '%s' not found in list:%s" % (name, _list))


def get_wsdl_classes(soap_namespace):
    from . import wsdl11, wsdl12
    if soap_namespace == ns.wsdl_soap:
        return wsdl11
    elif soap_namespace == ns.wsdl_soap12:
        return wsdl12
    else:
        raise NotImplementedError()
