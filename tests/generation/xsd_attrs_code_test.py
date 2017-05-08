from lxml import etree
from pythonic_testcase import (
    PythonicTestCase,
    assert_contains,
    assert_equals,
    assert_none,
    assert_raises
)

from soapfish import utils, xsd2py
from soapfish import testutil


class ComplexTypeAttributeUsageGenerationTest(PythonicTestCase):
    def setUp(self):
        xsd_str = utils.open_document('tests/assets/generation/attribute_usage.xsd')
        code = xsd2py.generate_code_from_xsd(xsd_str)
        self.schemas, self.symbols = testutil.generated_symbols(code)
        self.SampleType = self.symbols['SampleType']

    def test_can_specify_all_attributes(self):
        instance = self.SampleType(name='someName', value='someValue', type='someType')
        element = etree.Element('sample')
        instance.render(element, instance)

        assert_equals('someName', element.get('name'))
        assert_equals('someType', element.get('type'))
        assert_equals('someValue', element.get('value'))

    def test_can_omit_optional_attributes(self):
        instance = self.SampleType(name='someName')
        element = etree.Element('sample')
        instance.render(element, instance)

        assert_equals('someName', element.get('name'))
        assert_none(element.get('value'))
        assert_none(element.get('type'))

    def test_cannot_omit_required_attribute(self):
        instance = self.SampleType(value='someValue', type='someType')
        element = etree.Element('sample')

        with assert_raises(ValueError) as context:
            instance.render(element, instance)
        # the exception raised should mention the field is required
        assert_contains('required', str(context.caught_exception))


class AttributeGroupUsageGenerationTest(PythonicTestCase):
    def setUp(self):
        xsd_str = utils.open_document('tests/assets/generation/attrgroup_usage.xsd')
        self.code = xsd2py.generate_code_from_xsd(xsd_str)

    def test_can_specify_all_attributes(self):
        with testutil.import_code(self.code) as generated:
            instance = generated.SampleType(
                sampleAttrs=generated.SampleAttrs(name='someName', value='someValue', type='someType')
            )
            element = etree.Element('sample')
            instance.render(element, instance)

            assert_equals('someName', element.get('name'))
            assert_equals('someType', element.get('type'))
            assert_equals('someValue', element.get('value'))

    def test_can_omit_optional_attributes(self):
        with testutil.import_code(self.code) as generated:
            instance = generated.SampleType(sampleAttrs=generated.SampleAttrs(name='someName'))
            element = etree.Element('sample')
            instance.render(element, instance)

            assert_equals('someName', element.get('name'))
            assert_none(element.get('value'))
            assert_none(element.get('type'))

    def test_cannot_omit_required_attribute(self):
        with testutil.import_code(self.code) as generated:
            instance = generated.SampleType(sampleAttrs=generated.SampleAttrs(value='someValue', type='someType'))
            element = etree.Element('sample')

            with assert_raises(ValueError) as context:
                instance.render(element, instance)
            # the exception raised should mention the field is required
            assert_contains('required', str(context.caught_exception))
