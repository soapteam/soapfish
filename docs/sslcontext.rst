Mutual authentication with SSL
===============================

Consume service throug SSL is possible in soapfish, we use requests so you can expecify environment variables to change the behaivor of request in ssl context.

Possible variables:

- `REQUESTS_CA_CHECK` if false, don't verify the certificate 
- `REQUESTS_CA_PATH` set the Autority Certificate to be used to check certificates
- `REQUESTS_CERT_PATH` set path to certificate.
- `REQUESTS_KEY_PATH` set path to private key used to encript message

Also it's possible to set only `REQUESTS_CERT_PATH` in pem format with private key and certify without REQUESTS_KEY_PATH

.. warning:: Both get and post method are cover with environment variables

Using as Stub arguments
-------------------------

You can specify the same variables on stub class

.. code-block:: python

    class MyServiceStub(soap.Stub):
        SERVICE = SERVICE
        SCHEME = 'https'
        HOST = 'example.com'
        REQUESTS_CA_CHECK= False

or including mutual authenticacion with known Autority Certificate.


.. code-block:: python

    class MyServiceStub(soap.Stub):
        SERVICE = SERVICE
        SCHEME = 'https'
        HOST = 'example.com'
        REQUESTS_CA_PATH='/path/to/ca.crt'
        REQUESTS_CERT_PATH='/path/to/certificate.crt'
        REQUESTS_KEY_PATH='/path/to/key.pem'

.. warning:: The private key to your local certificate must be unencrypted. Currently, Requests does not support using encrypted keys.
