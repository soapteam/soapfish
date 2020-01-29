import unittest

from soapfish import xsd


class RefTest(unittest.TestCase):
    def test_can_render_references_to_groups(self):
        class Person(xsd.Group):
            name = xsd.Element(xsd.String)

        class Job(xsd.ComplexType):
            title = xsd.Element(xsd.String)
            person = xsd.Ref(Person)

        job = Job()
        job.person = Person(name='Foo Bar')
        self.assertEqual('Foo Bar', job.person.name)
        # TODO: actually I think the current state is invalid as title is missing?
        expected_xml = (
            b'<job>\n'
            b'  <name>Foo Bar</name>\n'
            b'</job>\n'
        )
        self.assertEqual(expected_xml, job.xml('job'))

    @unittest.skip('References to SimpleTypes are not yet implemented.')
    def test_can_render_references_to_simple_types(self):
        class Person(xsd.SimpleType):
            pass

        class Job(xsd.ComplexType):
            title = xsd.Element(xsd.String)
            # LATER: Check if that is actually the correct/expected syntax
            name = xsd.Ref(Person)

        job = Job()
        job.person = 'Foo Bar'
        self.assertEqual('Foo Bar', job.person)
        expected_xml = (
            b'<job>\n'
            b'  <name>Foo Bar</name>\n'
            b'</job>\n'
        )
        self.assertEqual(expected_xml, job.xml('job'))

    def test_can_render_references_to_complex_types(self):
        class Person(xsd.ComplexType):
            name = xsd.Element(xsd.String)

        class Job(xsd.ComplexType):
            title = xsd.Element(xsd.String)
            person = xsd.Ref(Person)

        job = Job()
        job.person = Person(name='Foo Bar')
        self.assertEqual('Foo Bar', job.person.name)
        expected_xml = (
            b'<job>\n'
            b'  <person>\n'
            b'    <name>Foo Bar</name>\n'
            b'  </person>\n'
            b'</job>\n'
        )
        self.assertEqual(expected_xml, job.xml('job'))
