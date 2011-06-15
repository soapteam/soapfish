# Create your views here.
from soapbox import xsd, soap

class GetStockPrice(xsd.ComplexType):
    company = xsd.Element(xsd.String, minOccurs=1)
    datetime = xsd.Element(xsd.DateTime)
    
class StockPrice(xsd.ComplexType):
    nillable = xsd.Element(xsd.Int,nillable=True)
    price = xsd.Element(xsd.Decimal(fractionDigits=2))
    
Schema = xsd.Schema(
      #Should be unique URL, can be any string.
      targetNamespace = "http://code.google.com/p/soapbox/stock.xsd",
      #Register all complex types to schema.
      complexTypes = [GetStockPrice, StockPrice],
      elements = {"getStockPrice":xsd.Element("GetStockPrice"), 
                  "stockPrice":xsd.Element("StockPrice")}              
)

def get_stock_price(request, gsp):
    print gsp.company, gsp.datetime
    return StockPrice(nillable=xsd.NIL,price=139.21)

get_stock_price_method = xsd.Method(
    function = get_stock_price,
    soapAction = "http://code.google.com/p/soapbox/stock/get_stock_price",
    input = "getStockPrice",
    output = "stockPrice",
    operationName = "GetStockPrice")

SERVICE = soap.Service(
    #WSDL targetNamespce
    targetNamespace = "http://code.google.com/p/soapbox/stock.wsdl",
    #The url were request should be send.
    location = "http://127.0.0.1:8000/stock",
    schema = Schema,
    methods = [get_stock_price_method])

from django.views.decorators.csrf import csrf_exempt
dispatch = csrf_exempt(soap.get_django_dispatch(SERVICE))
