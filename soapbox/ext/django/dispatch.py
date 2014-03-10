from soapbox.soap_dispatch import SOAPDispatcher, WsgiSoapApplication

# https://github.com/Polyconseil/django-viewsgi
from viewsgi import embed_wsgi


def get_django_dispatch(service):
    dispatcher = dispatch.DjangoSOAPDispatcher(service)
    wsgi = WsgiSoapApplication(dispatcher)
    return embed_wsgi(wsg)
