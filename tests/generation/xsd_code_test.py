import unittest

from lxml import etree

from soapfish import utils, xsd, xsd2py, xsdspec
from soapfish.testutil import generated_symbols


class XSDCodeGenerationTest(unittest.TestCase):

    def test_can_generate_code_for_simple_element(self):
        xml = utils.open_document('tests/assets/generation/simple_element.xsd')
        code = xsd2py.generate_code_from_xsd(xml)

        schemas, symbols = generated_symbols(code)
        self.assertTrue(schemas)
        self.assertEqual(len([s for s in symbols if s.startswith('Schema_')]), 1)

        self.assertEqual(['simpleElement'], list(schemas[0].elements))
        simple_element = schemas[0].elements['simpleElement']
        self.assertIsInstance(simple_element._type, xsd.String)

    @unittest.skip('References to simple elements not yet implemented')
    def test_can_generate_code_with_xsd_refs_to_simple_elements(self):
        xml = utils.open_document('tests/assets/generation/reference_simple.xsd')
        code = xsd2py.generate_code_from_xsd(xml)

        schemas, symbols = generated_symbols(code)
        self.assertTrue(schemas)
        # somehow we need to be able to have schemas with multiple possible
        # root elements
        self.assertEqual(len(symbols), 3)
        self.assertIn('Name', symbols.keys())
        self.assertIn('Job', symbols.keys())

        self.assertEqual({'job', 'name'}, list(schemas[0].elements))

        Job = symbols['Job']
        Name = symbols['Name']
        name_ref = Job.name
        # not sure if these assertions are correct but they should give you
        # the idea
        self.assertIsInstance(name_ref, xsd.Ref)
        self.assertEqual(name_ref._type, Name)

        job = Job()
        # Should not raise
        job.name = 'Foo'
        # probably we need to check some more stuff here

    @unittest.skip('References to elements with anonymous complex types are not yet implemented')
    def test_can_generate_code_with_xsd_refs_to_elements_with_anoynmous_complex_types(self):
        # The final test should have an object graph representation of the
        # schema below. Currently I don't know how to represent multiple
        # xs:elements in a schema without using ComplexTypes.
        # Maybe we should have a special type like AnonymousComplexType and
        # put that directly into schema.elements?
        xml = utils.open_document('tests/assets/generation/reference_complex.xsd')
        schema = xsdspec.Schema.parse_xmlelement(etree.fromstring(xml))
        code = xsd2py.schema_to_py(schema, ['xs'])

        schemas, symbols = generated_symbols(code)
        self.assertTrue(schemas)
        self.assertEqual(len(symbols), 3)
        self.assertIn('Person', symbols.keys())
        self.assertIn('Job', symbols.keys())

        self.assertEqual({'job', 'person'}, list(schemas[0].elements))

        Job = symbols['Job']
        Person = symbols['Person']
        person_ref = Job.person
        self.assertIsInstance(person_ref, xsd.Ref)
        self.assertEqual(person_ref._type, Person)

        job = Job()
        person = Person()
        person.name = 'Foo'
        job.person = person
        # Check generated XML
        # <job><person><name>Foo</name></person></job>

    # TODO: Add missing assertions to this test!
    def test_implicit_target_namespace(self):
        xml = utils.open_document('tests/assets/generation/implicit_namespace.xsd')
        schema = xsdspec.Schema.parse_xmlelement(etree.fromstring(xml))
        xsd2py.schema_to_py(schema, ['xs'], parent_namespace='http://site.example/ws/spec')

    @unittest.skip('list enumerations are not parsed correctly from xsd')
    def test_can_generate_list_enumeration(self):
        xml = utils.open_document('tests/assets/generation/enumeration.xsd')
        code = xsd2py.generate_code_from_xsd(xml)
        schemas, symbols = generated_symbols(code)
        self.assertTrue(schemas)
        self.assertEqual(len(symbols), 2)

        self.assertIs(issubclass(symbols['MyList'], xsd.List), True)

        my_list = symbols['MyList']()
        self.assertIs(my_list.accept(['B']), True)

    # TODO: Add missing assertions to this test!
    def test_can_generate_extension(self):
        xml = utils.open_document('tests/assets/generation/extension.xsd')
        code = xsd2py.generate_code_from_xsd(xml)
        schemas, symbols = generated_symbols(code)

    def test_can_generate_extension_imported(self):
        xml = utils.open_document('tests/assets/generation/extension_imported.xsd')
        code = xsd2py.generate_code_from_xsd(xml, cwd='tests/assets/generation')
        schemas, symbols = generated_symbols(code)
        self.assertTrue(schemas)

        base = symbols['Base']
        base.Field1
        try:
            base.Field2
        except AttributeError:
            pass
        else:
            self.fail('Unexpected base.Field2')

        ct = symbols['ComplexType']
        ct.Field1
        ct.Field2

    def test_can_generate_extension_of_type_with_special_chars(self):
        xml = utils.open_document('tests/assets/generation/extension_with_special_chars.xsd')
        code = xsd2py.generate_code_from_xsd(xml)
        schemas, symbols = generated_symbols(code)
        self.assertIn('BaseType_with_special_chars_123', symbols)
        self.assertEqual('BaseType_with_special_chars_123', symbols['ComplexType'].__base__.__name__)
