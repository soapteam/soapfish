from soapbox.soap_dispatch import SOAPDispatcher, WsgiSoapApplication

# https://github.com/Polyconseil/django-viewsgi
from viewsgi import embed_wsgi


def get_django_dispatch(url, service):
    dispatcher = dispatch.DjangoSOAPDispatcher(service)
    wsgi = WsgiSoapApplication({url, dispatcher})
    return embed_wsgi(wsg)
