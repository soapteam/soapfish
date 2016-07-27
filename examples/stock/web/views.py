# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from gen import SERVICE, SERVICE11, SERVICE12

from soapfish.django_ import django_dispatcher

dispatch11 = csrf_exempt(django_dispatcher(SERVICE11))
dispatch12 = csrf_exempt(django_dispatcher(SERVICE12))
ops_dispatch = csrf_exempt(django_dispatcher(SERVICE))
