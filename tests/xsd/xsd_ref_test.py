
from nose import SkipTest
from pythonic_testcase import PythonicTestCase, assert_equals

from soapfish import xsd


class RefTest(PythonicTestCase):
    def test_can_render_references_to_groups(self):
        class Person(xsd.Group):
            name = xsd.Element(xsd.String)

        class Job(xsd.ComplexType):
            title = xsd.Element(xsd.String)
            person = xsd.Ref(Person)

        job = Job()
        job.person = Person(name=u'Foo Bar')
        assert_equals(u'Foo Bar', job.person.name)
        # TODO: actually I think the current state is invalid as title is missing?
        expected_xml = (
            b'<job>\n'
            b'  <name>Foo Bar</name>\n'
            b'</job>\n'
        )
        assert_equals(expected_xml, job.xml('job'))

    def test_can_render_references_to_simple_types(self):
        raise SkipTest('References to SimpleTypes are not yet implemented.')

        class Person(xsd.SimpleType):
            pass

        class Job(xsd.ComplexType):
            title = xsd.Element(xsd.String)
            # LATER: Check if that is actually the correct/expected syntax
            name = xsd.Ref(Person)

        job = Job()
        job.person = u'Foo Bar'
        assert_equals(u'Foo Bar', job.person)
        expected_xml = (
            b'<job>\n'
            b'  <name>Foo Bar</name>\n'
            b'</job>\n'
        )
        assert_equals(expected_xml, job.xml('job'))

    def test_can_render_references_to_complex_types(self):
        class Person(xsd.ComplexType):
            name = xsd.Element(xsd.String)

        class Job(xsd.ComplexType):
            title = xsd.Element(xsd.String)
            person = xsd.Ref(Person)

        job = Job()
        job.person = Person(name=u'Foo Bar')
        assert_equals(u'Foo Bar', job.person.name)
        expected_xml = (
            b'<job>\n'
            b'  <person>\n'
            b'    <name>Foo Bar</name>\n'
            b'  </person>\n'
            b'</job>\n'
        )
        assert_equals(expected_xml, job.xml('job'))
