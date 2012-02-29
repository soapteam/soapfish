from lxml import etree
import keyword
import sys
import httplib2
import hashlib
from jinja2 import Environment
from xsdspec import Schema
from utils import removens, classyfiy, get_get_type, use, find_xsd_namepsace


TEMPLATE = '''\
{#- ---------- XSD Imports ---------- -#}

{%- for imp in schema.imports %}
{{ resolve_import(imp, known_namespaces) }}
{%- endfor %}

{#- ---------- SimpleType Generation ---------- -#}

{%- for st in schema.simpleTypes %}
{%- if st.restriction %}
class {{ st.name|class }}({{ st.restriction.base|type }}):
    \'\'\'
    \'\'\'
{%- if st.restriction.enumerations %}
    enumeration = [{% for enum in st.restriction.enumerations %}'{{ enum.value }}'{% if not loop.last %}, {% endif %}{% endfor %}]
{% endif %}
{%- if st.restriction.pattern %}
    pattern = r'{{ st.restriction.pattern.value }}'
{% endif %}
{%- if st.restriction.minInclusive %}
    minInclusive = r'{{ st.restriction.minInclusive.value }}'
{%- elif st.restriction.minExclusive %}
    minExclusive = r'{{ st.restriction.minExclusive.value }}'
{% endif %}
{%- if st.restriction.maxInclusive %}
    maxInclusive = r'{{ st.restriction.maxInclusive.value }}'
{%- elif st.restriction.maxExclusive %}
    maxExclusive = r'{{ st.restriction.maxExclusive.value }}'
{% endif %}
{%- if not st.restriction.enumerations and not st.restriction.pattern
        and not st.restriction.minInclusive and not st.restriction.minExclusive
        and not st.restriction.maxInclusive and not st.restriction.maxExclusive %}
    pass
{% endif %}
{% endif %}

{%- if st.list %}
class {{ st.name|class }}(xsd.List):
    \'\'\'
    \'\'\'
    pass
{%- endif %}
{%- endfor %}

{#- ---------- GROUOPS ---------- -#}

{%- for attrGroup in schema.attributeGroups %}
class {{ attrGroup.name|class }}(xsd.AttributeGroup):
    \'\'\'
    \'\'\'
    {%- for attribute in attrGroup.attributes %}
    {{ attribute.name }} = xsd.Attribute({{ attribute.type|type }}{% if attribute.use %}, use={{ attribute.use|use }}{% endif %})
    {%- endfor %}
{%- endfor %}

{%- for group in schema.groups %}
class {{ group.name|class }}(xsd.Group):
    \'\'\'
    \'\'\'
    {%- for element in group.sequence.elements %}
    {%- if element.ref %}
    {{ element.ref|removens }} = xsd.Element({{ element.ref|type }})
    {%- if element.ref|removens in keywords %}
    _{{ element.ref|removens }} = xsd.Element({{ element.type|type }}, tagname='{{ element.ref|removens }}')
    {%- else %}
    {{ element.ref|removens }} = xsd.Element({{ element.type|type }})
    {%- endif %}
    {%- else %}
    {%- if element.name in keywords %}
    _{{ element.name }} = xsd.Element({{ element.type|type }}, tagname='{{ element.name }}')
    {%- else %}
    {{ element.name }} = xsd.Element({{ element.type|type }})
    {%- endif %}
    {%- endif %}
    {%- endfor %}
{%- endfor %}

{#- ---------- ComplexTypes ---------- -#}

{% for ct in schema.complexTypes %}
{%- set content = ct %}
{%- if not ct.sequence and not ct.complexContent %}
class {{ ct.name|class }}(xsd.ComplexType):
    \'\'\'
    \'\'\'
{%- endif %}
{%- if ct.complexContent %}
    {%- if ct.complexContent.restriction %}
class {{ ct.name|class }}({{ ct.complexContent.restriction.base|type }}):
    \'\'\'
    \'\'\'
    INHERITANCE = xsd.Inheritance.RESTRICTION
    {%- set content = ct.complexContent.restriction %}
    {%- else %}
class {{ ct.name|class }}({{ ct.complexContent.extension.base|type }}):
    \'\'\'
    \'\'\'
    INHERITANCE = xsd.Inheritance.EXTENSION
    {%- set content = ct.complexContent.extension %}
    {%- endif %}
{%- elif ct.sequence %}
class {{ ct.name|class }}(xsd.ComplexType):
    \'\'\'
    \'\'\'
    INHERITANCE = None
    {%- set content = ct %}
{%- endif %}
{%- if content.sequence %}
    INDICATOR = xsd.Sequence
    {%- set elements = content.sequence.elements %}
{%- elif content.all %}
    INDICATOR = xsd.All
    {%- set elements = content.all.elements %}
{%- elif content.choice %}
    INDICATOR = xsd.Choice
    {%- set elements = content.choice.elements %}
{%- endif %}
{%- for attribute in content.attributes %}
    {%- if attribute.ref %}
    {{ attribute.ref|removens }} = xsd.Attribute({{ attribute.ref|type }})
    {%- else %}
    {{ attribute.name }} = xsd.Attribute({{ attribute.type|type }}{% if attribute.use %}, use={{ attribute.use|use }}{% endif %})
    {%- endif %}
{%- endfor %}
{%- for attrGroupRef in content.attributeGroups %}
    {{ attrGroupRef.ref|removens }} = xsd.Ref({{ attrGroupRef.ref|type }})
{%- endfor %}
{%- for element in elements %}
    {%- if element.type %}
    {%- if element.maxOccurs > 1 %}
    {%- if element.name + 's' in keywords %}
    _{{ element.name }}s = xsd.ListElement({{ element.type|type }}, '{{ element.name }}', tagname='{{ element.name }}s'{% if not element.minOccurs is none %}, minOccurs={{ element.minOccurs|upper }}{% endif %}{% if not element.maxOccurs is none %}, maxOccurs={{ element.maxOccurs|upper }}{% endif %}{% if element.nillable %}, nillable=True{% endif %})
    {%- else %}
    {{ element.name }}s = xsd.ListElement({{ element.type|type }}, '{{ element.name }}'{% if not element.minOccurs is none %}, minOccurs={{ element.minOccurs|upper }}{% endif %}{% if not element.maxOccurs is none %}, maxOccurs={{ element.maxOccurs|upper }}{% endif %}{% if element.nillable %}, nillable=True{% endif %})
    {%- endif %}
    {%- else %}
    {%- if element.name in keywords %}
    _{{ element.name }} = xsd.Element({{ element.type|type }}, tagname='{{ element.name }}'{% if not element.minOccurs is none %}, minOccurs={{ element.minOccurs|upper }}{% endif %}{% if element.nillable %}, nillable=True{% endif %})
    {%- else %}
    {{ element.name }} = xsd.Element({{ element.type|type }}{% if not element.minOccurs is none %}, minOccurs={{ element.minOccurs|upper }}{% endif %}{% if element.nillable %}, nillable=True{% endif %})
    {%- endif %}
    {%- endif %}
    {%- endif %}
    {%- if element.simpleType %}
    {%- if element.name in keywords %}
    _{{ element.name }} = xsd.{{ field_type }}({{ element.simpleType.restriction.base|type }}(
    {%- else %}
    {{ element.name }} = xsd.{{ field_type }}({{ element.simpleType.restriction.base|type }}(
    {%- endif %}
    {%- if element.simpleType.restriction.enumerations %}enumeration=[{% for enum in element.simpleType.restriction.enumerations %}'{{ enum.value }}'{% if not loop.last %}, {% endif %}{% endfor %}])
    {%- endif %}
    {%- if element.name in keywords %}tagname='{{ element.name }}',{% endif %}
    {%- if element.simpleType.restriction.minInclusive %}minInclusive={{ element.simpleType.restriction.minInclusive.value }},{% endif %}
    {%- if element.simpleType.restriction.maxInclusive %}maxInclusive={{ element.simpleType.restriction.maxInclusive.value }},{% endif %}
    {%- if element.simpleType.restriction.minExclusive %}minExclusive={{ element.simpleType.restriction.minExclusive.value }},{% endif %}
    {%- if element.simpleType.restriction.maxExclusive %}maxExclusive={{ element.simpleType.restriction.maxExclusive.value }},{% endif %}
    {%- if element.simpleType.restriction.fractionDigits %}fractionDigits={{ element.simpleType.restriction.fractionDigits.value }},{% endif %}
    {%- if element.simpleType.restriction.totalDigits %}totalDigits={{ element.simpleType.restriction.totalDigits.value }},{% endif %}
    {%- if element.simpleType.restriction.pattern %}pattern={{ element.simpleType.restriction.pattern.value }},{% endif %})
    {%- endif %}
    {%- if element.ref %}{{ element.ref|removens }} = xsd.Ref({{ element.ref|type }}){% endif %}
{%- endfor %}
{%- if content.sequence %}

    @classmethod
    def create(cls{% for e in elements %}{% if e.minOccurs == 1 or e.minOccurs == None %}, {{ e.name }}{% endif %}{% endfor %}):
        instance = cls()
        {%- for e in elements %}
        {%- if e.minOccurs == 1 or e.minOccurs == None %}
        instance.{{ e.name }} = {{ e.name }}
        {%- endif %}
        {%- endfor %}
        return instance

{% endif %}
{%- endfor %}

{#- ---------- complexTypes defined in elements ---------- -#}

{%- for element in schema.elements %}
    {%- if element.complexType %}

{%- set ct = element.complexType %}
{%- set content = element.complexType %}

{%- if not ct.sequence and not ct.complexContent %}
class {{ element.name|class }}(xsd.ComplexType):
    \'\'\'
    \'\'\'
{%- endif %}
{%- if ct.complexContent %}
    {%- if ct.complexContent.restriction %}
class {{ ct.name|class }}({{ ct.complexContent.restriction.base|type }}):
    \'\'\'
    \'\'\'
    INHERITANCE = xsd.Inheritance.RESTRICTION
    {%- set content = ct.complexContent.restriction %}
    {%- else %}
class {{ ct.name|class }}({{ ct.complexContent.extension.base|type }}):
    \'\'\'
    \'\'\'
    INHERITANCE = xsd.Inheritance.EXTENSION
    {%- set content = ct.complexContent.extension %}
    {%- endif %}
{%- elif ct.sequence %}
class {{ element.name|class }}(xsd.ComplexType):
    \'\'\'
    \'\'\'
    INHERITANCE = None
    {%- set content = ct %}
{%- endif %}
{%- if content.sequence %}
    INDICATOR = xsd.Sequence
    {%- set elements = content.sequence.elements %}
{%- elif content.all %}
    INDICATOR = xsd.All
    {%- set elements = content.all.elements %}
{%- elif content.choice %}
    INDICATOR = xsd.Choice
    {%- set elements = content.choice.elements %}
{%- endif %}
{%- for attribute in content.attributes %}
    {%- if attribute.ref %}
    {{ attribute.ref|removens }} = xsd.Attribute({{ attribute.ref|type }})
    {%- else %}
    {{ attribute.name }} = xsd.Attribute({{ attribute.type|type }}{% if attribute.use %}, use={{ attribute.use|use }}{% endif %})
    {%- endif %}
{%- endfor %}
{%- for attrGroupRef in content.attributeGroups %}
    {{ attrGroupRef.ref|removens }} = xsd.Ref({{ attrGroupRef.ref|type }})
{%- endfor %}
{%- for element in elements %}
    {%- if element.maxOccurs > 1 %}
        {%- set field_type = 'ListElement' %}
    {%- else %}
        {%- set field_type = 'Element' %}
    {%- endif %}
    {%- if element.type %}
    {%- if element.name in keywords %}
    _{{ element.name }} = xsd.{{ field_type }}({{ element.type|type }}, tagname='{{ element.name }}'{% if not element.minOccurs is none %}, minOccurs={{ element.minOccurs|upper }}{% endif %}{% if not element.maxOccurs is none %}, maxOccurs={{ element.maxOccurs|upper }}{% endif %}{% if element.nillable %}, nillable=True{% endif %})
    {%- else %}
    {{ element.name }} = xsd.{{ field_type }}({{ element.type|type }}{% if not element.minOccurs is none %}, minOccurs={{ element.minOccurs|upper }}{% endif %}{% if not element.maxOccurs is none %}, maxOccurs={{ element.maxOccurs|upper }}{% endif %}{% if element.nillable %}, nillable=True{% endif %})
    {%- endif %}
    {%- endif %}
    {%- if element.simpleType %}
    {%- if element.name in keywords %}
    _{{ element.name }} = xsd.Element({{ element.simpleType.restriction.base|type }}(
    {%- else %}
    {{ element.name }} = xsd.Element({{ element.simpleType.restriction.base|type }}(
    {%- endif %}
    {%- if element.simpleType.restriction.enumerations %}
    enumeration=[{% for enum in element.simpleType.restriction.enumerations %}'{{ enum.value }}'{% if not loop.last %}, {% endif %}{% endfor %}])
    {%- endif %}
    {%- if element.name in keywords %}tagname='{{ element.name }}',{% endif %}
    {%- if element.simpleType.restriction.minInclusive %}minInclusive={{ element.simpleType.restriction.minInclusive.value }},{% endif %}
    {%- if element.simpleType.restriction.maxInclusive %}maxInclusive={{ element.simpleType.restriction.maxInclusive.value }},{% endif %}
    {%- if element.simpleType.restriction.minExclusive %}minExclusive={{ element.simpleType.restriction.minExclusive.value }},{% endif %}
    {%- if element.simpleType.restriction.maxExclusive %}maxExclusive={{ element.simpleType.restriction.maxExclusive.value }},{% endif %}
    {%- if element.simpleType.restriction.fractionDigits %}fractionDigits={{ element.simpleType.restriction.fractionDigits.value }},{% endif %}
    {%- if element.simpleType.restriction.totalDigits %}totalDigits={{ element.simpleType.restriction.totalDigits.value }},{% endif %}
    {%- if element.simpleType.restriction.pattern %}pattern={{ element.simpleType.restriction.pattern.value }},{% endif %})
    {%- endif %}
    {%- if element.ref %}
    {{ element.ref|removens }} = xsd.Ref({{ element.ref|type }})
    {%- endif %}
{%- endfor %}
{%- if content.sequence %}

    @classmethod
    def create(cls{%- for e in elements %}{% if e.minOccurs == 1 or e.minOccurs == None %}, {{ e.name }}{% endif %}{% endfor %}):
        instance = cls()
        {%- for e in elements %}
        {%- if e.minOccurs == 1 or e.minOccurs == None%}
        instance.{{ e.name }} = {{ e.name }}
        {%- endif %}
        {%- endfor %}
        return instance

{% endif %}
{%- endif %}
{%- endfor %}

Schema_{{ schema_name(schema.targetNamespace) }} = xsd.Schema(
    imports=[{% for i in schema.imports %}Schema_{{ schema_name(i.namespace) }}{% if not loop.last %}, {% endif %}{% endfor %}],
    targetNamespace='{{ schema.targetNamespace }}',
    {%- if location %}
    location='{{ location }}',{% endif %}
    elementFormDefault='{{ schema.elementFormDefault }}',
    simpleTypes=[{% for st in schema.simpleTypes %}{{ st.name|class }}{% if not loop.last %}, {% endif %}{% endfor %}],
    attributeGroups=[{% for ag in schema.attributeGroups %}{{ ag.name|class }}{% if not loop.last %}, {% endif %}{% endfor %}],
    groups=[{% for g in schema.groups %}{{ g.name|class }}{% if not loop.last %}, {% endif %}{% endfor %}],
    complexTypes=[{% for ct in schema.complexTypes %}{{ ct.name|class }}{% if not loop.last %}, {% endif %}{% endfor %}],
    elements={{ '{' }}{% for e in schema.elements %}'{{ e.name }}': xsd.Element({% if e.type %}{{ e.type|type }}{% else %}{{ e.name|class }}(){% endif %}){% if not loop.last %}, {% endif %}{% endfor %}{{ '}' }},
)
'''


def schema_name(namespace):
    return hashlib.sha512(namespace).hexdigest()[0:5]


def generate_code_from_xsd(xmlelement, known_namespaces=None, location=None):
    if known_namespaces is None:
        known_namespaces = []
    XSD_NAMESPACE = find_xsd_namepsace(xmlelement.nsmap)

    schema = Schema.parse_xmlelement(xmlelement)
    if schema.targetNamespace in known_namespaces:
        return ""
    else:
        return schema_to_py(schema, XSD_NAMESPACE, known_namespaces, location)


def schema_to_py(schema, xsd_namespce, known_namespaces=None, location=None):
    if known_namespaces is None:
        known_namespaces = []
    known_namespaces.append(schema.targetNamespace)

    environment = Environment()
    environment.filters["class"] = classyfiy
    environment.filters["removens"] = removens
    environment.filters["use"] = use
    environment.filters["type"] = get_get_type(xsd_namespce)
    environment.globals["resolve_import"] = resolve_import
    environment.globals["known_namespaces"] = known_namespaces
    environment.globals["schema_name"] = schema_name
    environment.globals["location"] = location
    environment.globals["keywords"] = keyword.kwlist
    return environment.from_string(TEMPLATE).render(schema=schema)


def resolve_import(xsdimport, known_namespaces):
    xml = open_document(xsdimport.schemaLocation)
    xmlelement = etree.fromstring(xml)
    return generate_code_from_xsd(xmlelement, known_namespaces, xsdimport.schemaLocation)


def open_document(document_address):
    if document_address.startswith("http:"):
        http = httplib2.Http()
        _, content = http.request(document_address)
        return content
    else:
        return open(document_address).read()


def main():
    if len(sys.argv) != 2:
        print "use: xsd2py <path to xsd>"
        return
    xml = open(sys.argv[1]).read()
    xmlelement = etree.fromstring(xml)
    print """from soapbox import xsd
from soapbox.xsd import UNBOUNDED"""
    print generate_code_from_xsd(xmlelement)

if __name__ == "__main__":
    main()
