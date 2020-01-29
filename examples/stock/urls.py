from django.conf.urls import url

urlpatterns = [
    url(r'^stock/soap11$', 'stock.web.views.dispatch11'),
    url(r'^stock/soap12$', 'stock.web.views.dispatch12'),
    url(r'^ws/ops$', 'stock.web.views.ops_dispatch'),
]
