from soapbox.soap_dispatch import SOAPDispatcher, WsgiSoapApplication

from wsgiutil import embed_wsgi


def get_django_dispatch(url, service):
    dispatcher = dispatch.DjangoSOAPDispatcher(service)
    wsgi = WsgiSoapApplication({url, dispatcher})
    return embed_wsgi(wsg)
