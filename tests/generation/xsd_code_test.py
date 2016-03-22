import unittest

from lxml import etree
from pythonic_testcase import *  # noqa

from soapfish import utils, xsd, xsd2py, xsdspec
from soapfish.testutil import generated_symbols


class XSDCodeGenerationTest(PythonicTestCase):

    def test_can_generate_code_for_simple_element(self):
        xml = utils.open_document('tests/assets/generation/simple_element.xsd')
        code = xsd2py.generate_code_from_xsd(xml)

        schema, new_symbols = generated_symbols(code)
        assert_not_none(schema)
        assert_length(1, new_symbols)

        assert_equals(['simpleElement'], list(schema.elements))
        simple_element = schema.elements['simpleElement']
        assert_isinstance(simple_element._type, xsd.String)

    @unittest.skip('References to simple elements not yet implemented')
    def test_can_generate_code_with_xsd_refs_to_simple_elements(self):
        xml = utils.open_document('tests/assets/generation/reference_simple.xsd')
        code = xsd2py.generate_code_from_xsd(xml)

        schema, new_symbols = generated_symbols(code)
        assert_not_none(schema)
        # somehow we need to be able to have a schema with multiple possible
        # root elements
        assert_length(3, new_symbols)
        assert_contains('Name', new_symbols.keys())
        assert_contains('Job', new_symbols.keys())

        assert_equals(set(['name', 'job']), list(schema.elements))

        Job = new_symbols['Job']
        Name = new_symbols['Name']
        name_ref = Job.name
        # not sure if these assertions are correct but they should give you
        # the idea
        assert_isinstance(name_ref, xsd.Ref)
        assert_equals(name_ref._type, Name)

        job = Job()
        # Should not raise
        job.name = u'Foo'
        # probably we need to check some more stuff here

    @unittest.skip('References to elements with anonymous complex types are not yet implemented')
    def test_can_generate_code_with_xsd_refs_to_elements_with_anoynmous_complex_types(self):
        # The final test should have an object graph representation of the
        # schema below. Currently I don't know how to represent multiple
        # xs:elements in a schema without using ComplexTypes.
        # Maybe we should have a special type like AnonymousComplexType and
        # put that directly into schema.elements?
        xml = utils.open_document('tests/assets/generation/reference_complex.xsd')
        generated_schema = xsdspec.Schema.parse_xmlelement(etree.fromstring(xml))
        code = xsd2py.schema_to_py(generated_schema, ['xs'])

        schema, new_symbols = generated_symbols(code)
        assert_not_none(schema)
        assert_length(3, new_symbols)
        assert_contains('Person', new_symbols.keys())
        assert_contains('Job', new_symbols.keys())

        assert_equals(set(['person', 'job']), list(schema.elements))

        Job = new_symbols['Job']
        Person = new_symbols['Person']
        person_ref = Job.person
        assert_isinstance(person_ref, xsd.Ref)
        assert_equals(person_ref._type, Person)

        job = Job()
        person = Person()
        person.name = 'Foo'
        job.person = person
        # Check generated XML
        # <job><person><name>Foo</name></person></job>

    def test_implicit_target_namespace(self):
        xml = utils.open_document('tests/assets/generation/implicit_namespace.xsd')
        generated_schema = xsdspec.Schema.parse_xmlelement(etree.fromstring(xml))
        xsd2py.schema_to_py(generated_schema, ['xs'],
                            parent_namespace='http://site.example/ws/spec')

    @unittest.skip('list enumerations are not parsed correctly from xsd')
    def test_can_generate_list_enumeration(self):
        xml = utils.open_document('tests/assets/generation/enumeration.xsd')
        code = xsd2py.generate_code_from_xsd(xml)

        schema, new_symbols = generated_symbols(code)
        assert_not_none(schema)
        assert_length(2, new_symbols)

        assert_true(issubclass(new_symbols['MyList'], xsd.List))

        my_list = new_symbols['MyList']()
        assert_equals(my_list.accept(['B']), True)

    def test_can_generate_extension(self):
        xml = utils.open_document('tests/assets/generation/extension.xsd')
        code = xsd2py.generate_code_from_xsd(xml)
        schema, new_symbols = generated_symbols(code)
