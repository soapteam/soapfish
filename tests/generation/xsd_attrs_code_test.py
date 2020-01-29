import unittest

from lxml import etree

from soapfish import testutil, utils, xsd2py


class ComplexTypeAttributeUsageGenerationTest(unittest.TestCase):
    def setUp(self):
        xsd_str = utils.open_document('tests/assets/generation/attribute_usage.xsd')
        code = xsd2py.generate_code_from_xsd(xsd_str)
        self.schemas, self.symbols = testutil.generated_symbols(code)
        self.SampleType = self.symbols['SampleType']

    def test_can_specify_all_attributes(self):
        instance = self.SampleType(name='someName', value='someValue', type='someType')
        element = etree.Element('sample')
        instance.render(element, instance)

        self.assertEqual('someName', element.get('name'))
        self.assertEqual('someType', element.get('type'))
        self.assertEqual('someValue', element.get('value'))

    def test_can_omit_optional_attributes(self):
        instance = self.SampleType(name='someName')
        element = etree.Element('sample')
        instance.render(element, instance)

        self.assertEqual('someName', element.get('name'))
        self.assertIsNone(element.get('value'))
        self.assertIsNone(element.get('type'))

    def test_cannot_omit_required_attribute(self):
        instance = self.SampleType(value='someValue', type='someType')
        element = etree.Element('sample')

        with self.assertRaises(ValueError) as cm:
            instance.render(element, instance)
        # the exception raised should mention the field is required
        self.assertIn('required', str(cm.exception))


class AttributeGroupUsageGenerationTest(unittest.TestCase):
    def setUp(self):
        xsd_str = utils.open_document('tests/assets/generation/attrgroup_usage.xsd')
        self.code = xsd2py.generate_code_from_xsd(xsd_str)

    def test_can_specify_all_attributes(self):
        with testutil.import_code(self.code) as generated:
            instance = generated.SampleType(
                sampleAttrs=generated.SampleAttrs(name='someName', value='someValue', type='someType'),
            )
            element = etree.Element('sample')
            instance.render(element, instance)

            self.assertEqual('someName', element.get('name'))
            self.assertEqual('someType', element.get('type'))
            self.assertEqual('someValue', element.get('value'))

    def test_can_omit_optional_attributes(self):
        with testutil.import_code(self.code) as generated:
            instance = generated.SampleType(sampleAttrs=generated.SampleAttrs(name='someName'))
            element = etree.Element('sample')
            instance.render(element, instance)

            self.assertEqual('someName', element.get('name'))
            self.assertIsNone(element.get('value'))
            self.assertIsNone(element.get('type'))

    def test_cannot_omit_required_attribute(self):
        with testutil.import_code(self.code) as generated:
            instance = generated.SampleType(sampleAttrs=generated.SampleAttrs(value='someValue', type='someType'))
            element = etree.Element('sample')

            with self.assertRaises(ValueError) as cm:
                instance.render(element, instance)
            # the exception raised should mention the field is required
            self.assertIn('required', str(cm.exception))
