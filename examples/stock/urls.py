from django.urls import path

urlpatterns = [
    path('stock/soap11', 'stock.web.views.dispatch11'),
    path('stock/soap12', 'stock.web.views.dispatch12'),
    path('ws/ops', 'stock.web.views.ops_dispatch'),
]
