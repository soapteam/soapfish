from .. import xsd
from ..core import SOAPResponse
from ..lib.attribute_dict import AttrDict
from ..soap import Service, SOAPVersion

__all__ = ['echo_handler', 'echo_service', 'EchoInputHeader', 'EchoOutputHeader']


class EchoType(xsd.ComplexType):
    INHERITANCE = None
    INDICATOR = xsd.Sequence
    value = xsd.Element(xsd.String, nillable=False)

    @classmethod
    def create(cls, value):
        instance = cls()
        instance.value = value
        return instance


def echo_handler():
    state = AttrDict(was_called=False)

    def _handler(request, input_):
        state.update({
            'was_called': True,
            'request': request,
            'input_': input_,
            'input_header': request.soap_header,
        })
        return SOAPResponse(EchoType.create(input_.value))
    return _handler, state


class InputVersion(xsd.String):
    pass


class OutputVersion(xsd.String):
    pass


class EchoInputHeader(xsd.ComplexType):
    InputVersion = xsd.Element(InputVersion)


class EchoOutputHeader(xsd.ComplexType):
    OutputVersion = xsd.Element(OutputVersion)


def echo_service(handler=None, input_header=None, output_header=None):
    if handler is None:
        handler, handler_state = echo_handler()

    EchoSchema = xsd.Schema(
        'http://soap.example/echo/types',
        elementFormDefault=xsd.ElementFormDefault.UNQUALIFIED,
        simpleTypes=(InputVersion, OutputVersion),
        complexTypes=(EchoType, EchoInputHeader, EchoOutputHeader),
        elements={
            'echoRequest': xsd.Element(EchoType),
            'echoResponse': xsd.Element(EchoType),
            'InputVersion': xsd.Element(InputVersion),
            'OutputVersion': xsd.Element(OutputVersion),
        },
    )
    echo_method = xsd.Method(function=handler,
                             soapAction='echo',
                             input='echoRequest',
                             inputPartName='input_',
                             input_header=input_header,
                             output='echoResponse',
                             output_header=output_header,
                             outputPartName='result',
                             operationName='echoOperation',
                             )
    return Service(
        name='TestService',
        targetNamespace='http://soap.example/echo',
        location='http://soap.example/ws',
        schemas=[EchoSchema],
        version=SOAPVersion.SOAP11,
        methods=[echo_method],
    )
