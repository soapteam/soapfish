from . import namespaces as ns


# --- Functions ---------------------------------------------------------------
def get_by_name(_list, fullname):
    name = fullname.split(':')[-1]
    for item in _list:
        if item.name == name:
            return item
    raise ValueError("Item '%s' not found in list:%s" % (name, _list))


def get_message_header(definitions, binding, operation, x):
    assert x in ('input', 'output')
    obj = getattr(operation, x, None)
    if obj is None:
        return None
    parts = []
    for header in obj.headers:
        message = get_by_name(definitions.messages, header.message)
        parts.append(get_by_name(message.parts, header.part))
    return parts


def get_message_object(definitions, binding, operation, x):
    assert x in ('input', 'output')
    pt = get_by_name(definitions.portTypes, binding.type)
    pto = get_by_name(pt.operations, operation.name)
    obj = getattr(pto, x, None)
    if obj is None:
        return None
    return get_by_name(definitions.messages, obj.message)


def get_wsdl_classes(soap_namespace):
    from . import wsdl11, wsdl12
    if soap_namespace == ns.wsdl_soap:
        return wsdl11
    elif soap_namespace == ns.wsdl_soap12:
        return wsdl12
    else:
        raise NotImplementedError
