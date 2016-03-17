Middlewares
===========


Middlewares Overview
--------------------

The soapfish library implements a version of the Rack protocol. As a result, a soapfish dispatcher can have middlewares that may inspect, analyze, or modify the application environment, request, and response before and/or after the method call.


Middlewares Architecture
''''''''''''''''''''''''

Think of a soapfish dispatcher as an onion. Each layer of the onion is a middleware. When you invoke the dispatcher dispatch() method, the outer-most middleware layer is invoked first. When ready, that middleware layer is responsible for optionally invoking the next middleware layer that it surrounds. This process steps deeper into the onion - through each middleware layer - until the service method is invoked. This stepped process is possible because each middleware layer are callable. When you add new middleware to the dispatcher, the added middleware will become a new outer layer and surround the previous outer middleware layer (if available) or the service method call itself.


Dispatcher Reference
''''''''''''''''''''

The purpose of a middleware is to inspect, analyze, or modify the application environment, request, and response before and/or after the service method is invoked. It is easy for each middleware to obtain references to the primary dispatcher, its environment, its request, and its response:

.. code-block:: python

    def my_middleware(request, next_call):
        request.dispatcher      # the dispatcher
        request.environ         # the wsgi environment
        request.method          # the service method to be invoked
        request.http_content    # the raw http content
        request.soap_body       # the parsed soap body
        request.soap_header     # the parsed soap header

Changes made to the environment, request, and response objects will propagate immediately throughout the application and its other middleware layers.


Next Middleware Reference
'''''''''''''''''''''''''

Each middleware layer also has a reference to the next inner middleware layer to call with next_call. It is each middleware’s responsibility to optionally call the next middleware. Doing so will allow the request to complete its full life-cycle. If a middleware layer chooses not to call the next inner middleware layer, further inner middleware and the service method itself will not be run.

.. code-block:: python

    def my_middleware(request, next_call):
        return next_call(request)  # optionally call the next middleware


How to Use Middleware
---------------------

On the dispatcher instantiation, use the `middlewares` parameter to give a list of middleware, the first middleware in the list will be called first, it is the outer onion.
This is also possible to add middlewares by modifying the list `dispatcher.middlewares`.


Example Middleware
''''''''''''''''''

This example middleware will log the client IP address.

.. code-block:: python

    logger = logging.getLogger(__name__)
    def get_client_address(request, next_call):
        # retrieve ip address
        try:
            ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
        except KeyError:
            ip = request.environ['REMOTE_ADDR']
        # log the ip address
        logger.info('Received request from %s' % str(ip))
        # call next middleware
        return next_call(request)


Add Middleware
''''''''''''''

.. code-block:: python

    dispatcher = SOAPDispatcher(service, middlewares=[get_client_address])
    # or after instantiation

    # add an outer middleware
    dispatcher.middleware.insert(0, get_client_address)
    # add an inside middleware
    dispatcher.middlewate.append(get_client_address)


When the example dispatcher above is invoked, the client IP address will be logged.

How to Write Middleware
-----------------------

Middleware must be a callable accepting 2 parameters `request` and `next_call` with these exact names. The callable must return a soapfish response object.
You are encouraged to look at soapfish built-in middleware for working examples, e.g. `soapfish.middlewares.ExceptionToSoapFault` or `soapfish.middlewares.ExceptionLogger`.

This example is the most simple implementation of middleware.

.. code-block:: python

    def my_middleware(request, next_call):
        return next_call(request)

    class MyMiddlewate:
        def __call__(self, request, next_call):
            return next_call(request)
