
from soapbox import xsd
from soapbox.lib.pythonic_testcase import *


class XSDRefTest(PythonicTestCase):
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
        expected_xml = unicode('<job>\n'
            '  <name>Foo Bar</name>\n'
            '</job>\n'
        )
        assert_equals(expected_xml, job.xml('job'))
    
    def test_can_render_references_to_simple_types(self):
        self.skipTest('References to SimpleTypes are not yet implemented.')
        class Person(xsd.SimpleType):
            pass
        
        class Job(xsd.ComplexType):
            title = xsd.Element(xsd.String)
            # LATER: Check if that is actually the correct/expected syntax
            name = xsd.Ref(Person)
        
        job = Job()
        job.person = u'Foo Bar'
        assert_equals(u'Foo Bar', job.person)
        expected_xml = unicode('<job>\n'
            '  <name>Foo Bar</name>\n'
            '</job>\n'
        )
        assert_equals(expected_xml, job.xml('job'))

