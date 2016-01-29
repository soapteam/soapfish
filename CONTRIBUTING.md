How to Contribute
===================

Contributions to the project can take many forms:

** Document missing features **
I won't even pretend to understand the XML/XSD semantics completely so there is
a good chance I missed something.
You can help by submitting examples of XML (with the according schema) which
soapfish currently can not handle. Ideally you'd write a unit test which clearly
demonstrates the failure.

Please try to minimize the sample as much as possible. I know this can be
time-consuming but otherwise another developer has to do it, taking away
precious development time.


** Implement missing features **
Well, of course that's most helpful.

Some advice about the order in which new features should be implemented:
1. Ensure that you can express the XSD schema using the classes from
   soapfish.xsdspec. This is the actual schema representation without any
   semantic sugar.
2. Build your schema in soapfish.xsd elements which is the high-level API. Try
   to build the object graph as you need.
3. Ensure that the assigned values in the object graph can be parsed and
   serialized to XML.
4. Implement XSD generation using your object graph.
5. Implement code-generation based on a pre-built XSD representing your
   use-case.

