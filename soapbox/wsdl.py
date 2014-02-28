# -*- coding: utf-8 -*-

from . import xsd, xsdspec


# --- Functions ---------------------------------------------------------------
def get_by_name(_list, fullname):
    name = fullname.split(':')[-1]
    for item in _list:
        if item.name == name:
            return item
    raise ValueError("Item '%s' not found in list:%s" % (name, _list))


def get_wsdl_classes(soap_namespace):
    from . import wsdl11, wsdl12
    if soap_namespace == wsdl11.wsdl11_soap_ns:
        return wsdl11
    elif soap_namespace == wsdl12.wsdl11_soap12_ns:
        return wsdl12
    else:
        raise NotImplementedError()
