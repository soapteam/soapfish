# Create your views here.
from soapbox import xsd, soap
from soapbox.soap import SOAPVersion

class GetStockPrice(xsd.ComplexType):
    company = xsd.Element(xsd.String, minOccurs=1)
    datetime = xsd.Element(xsd.DateTime)
    
class StockPrice(xsd.ComplexType):
    nillable = xsd.Element(xsd.Int,nillable=True)
    prices = xsd.ListElement(xsd.Decimal(fractionDigits=2),tagname="price",minOccurs=0,maxOccurs=xsd.UNBOUNDED,nillable=True)
    
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
    sp = StockPrice(nillable=xsd.NIL)
    sp.prices.append(13.29)
    sp.prices.append(4.56)
    sp.prices.append(xsd.NIL)
    return sp

get_stock_price_method = xsd.Method(
    function = get_stock_price,
    soapAction = "http://code.google.com/p/soapbox/stock/get_stock_price",
    input = "getStockPrice",
    output = "stockPrice",
    operationName = "GetStockPrice")

SERVICE11 = soap.Service(
    #WSDL targetNamespce
    targetNamespace = "http://code.google.com/p/soapbox/stock.wsdl",
    version = SOAPVersion.SOAP11,
    #The url were request should be send.
    location = "http://127.0.0.1:8000/stock/soap11",
    schema = Schema,
    methods = [get_stock_price_method])

SERVICE12 = soap.Service(
    #WSDL targetNamespce
    targetNamespace = "http://code.google.com/p/soapbox/stock.wsdl",
    version = SOAPVersion.SOAP12,
    #The url were request should be send.
    location = "http://127.0.0.1:8000/stock/soap12",
    schema = Schema,
    methods = [get_stock_price_method])

from django.views.decorators.csrf import csrf_exempt
dispatch11 = csrf_exempt(soap.get_django_dispatch(SERVICE11))
dispatch12 = csrf_exempt(soap.get_django_dispatch(SERVICE12))
