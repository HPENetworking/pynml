# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
NML specification definition and generation module.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

import logging
from collections import OrderedDict
from os.path import abspath, normpath, dirname, join

from inflection import parameterize, underscore, camelize, pluralize
from jinja2 import FunctionLoader, Environment, StrictUndefined


log = logging.getLogger(__name__)


NML_SPEC = {
    'classes': [
        {
            'name': 'Network Object',
            'parent': None,
            'brief': 'FIXME: Network Object brief documentation',
            'doc': 'FIXME: Network Object documentation',
            'abstract': True,
            'attributes': [
                {
                    'name': 'name',
                    'property': True,
                    'nml_attribute': 'name',
                    'semantic_type': 'string',
                    'type': 'str',
                    'default': (
                        '\'{}<{}>\'.format(\n'
                        '                '
                        'self.__class__.__name__, str(id(self))\n'
                        '            '
                        ')'
                    ),
                    'default_arg': 'None',
                    'validation': '%s',
                    'doc': 'Human readable string name'
                },
                {
                    'name': 'identifier',
                    'property': True,
                    'nml_attribute': 'id',
                    'semantic_type': 'URI',
                    'type': 'str',
                    'default': 'str(id(self))',
                    'default_arg': 'None',
                    'validation': 'is_valid_uri(%s)',
                    'doc': 'Persistent globally unique URI'
                },
                {
                    'name': 'version',
                    'property': True,
                    'nml_attribute': 'version',
                    'semantic_type': 'timestamp',
                    'type': 'str',
                    'default': (
                        'datetime.now().replace(microsecond=0).isoformat()'
                    ),
                    'default_arg': 'None',
                    'validation': None,  # FIXME
                    'doc': 'Time stamp formatted as ISO 8601'
                },
            ],
            'relations': [
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: existsDuring documentation'
                },
                {
                    'name': 'isAlias',
                    'with': ['Network Object'],
                    'cardinality': '+',
                    'doc': 'FIXME: isAlias documentation'
                },
                {
                    'name': 'locatedAt',
                    'with': ['Location'],
                    'cardinality': '1',
                    'doc': 'FIXME: locatedAt documentation'
                },
            ]
        },
        {
            'name': 'Node',
            'parent': 'Network Object',
            'brief': 'FIXME: Node brief documentation',
            'doc': 'FIXME: Node documentation',
            'abstract': False,
            'attributes': [
            ],
            'relations': [
                {
                    'name': 'hasInboundPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: hasInboundPort documentation'
                },
                {
                    'name': 'hasOutboundPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: hasOutboundPort documentation'
                },
                {
                    'name': 'hasService',
                    'with': ['Switching Service'],
                    'cardinality': '+',
                    'doc': 'FIXME: hasService documentation'
                },
                {
                    'name': 'implementedBy',
                    'with': ['Node'],
                    'cardinality': '+',
                    'doc': 'FIXME: implementedBy documentation'
                },
            ]
        },
        {
            'name': 'Port',
            'parent': 'Network Object',
            'brief': 'FIXME: Port brief documentation',
            'doc': 'FIXME: Port documentation',
            'abstract': False,
            'attributes': [
                {
                    'name': 'encoding',
                    'property': True,
                    'nml_attribute': 'encoding',
                    'semantic_type': 'URI',
                    'type': 'str',
                    'default': '\'FIXME: Provide default\'',
                    'default_arg': 'None',
                    'validation': 'is_valid_uri(%s)',
                    'doc': (
                        'Format of the data streaming through the port as an '
                        'URI'
                    )
                },
            ],
            'relations': [
                {
                    'name': 'hasLabel',
                    'with': ['Label'],
                    'cardinality': '1',
                    'doc': 'FIXME: hasLabel documentation'
                },
                {
                    'name': 'hasService',
                    'with': ['Adaptation Service', 'De-adaptation Service'],
                    'cardinality': '+',
                    'doc': 'FIXME: hasService documentation'
                },
                {
                    'name': 'isSink',
                    'with': ['Link'],
                    'cardinality': '+',
                    'doc': 'FIXME: isSink documentation'
                },
                {
                    'name': 'isSource',
                    'with': ['Link'],
                    'cardinality': '+',
                    'doc': 'FIXME: isSource documentation'
                },
            ]
        },
        {
            'name': 'Link',
            'parent': 'Network Object',
            'brief': 'FIXME: Link brief documentation',
            'doc': 'FIXME: Link documentation',
            'abstract': False,
            'attributes': [
                {
                    'name': 'encoding',
                    'property': True,
                    'nml_attribute': 'encoding',
                    'semantic_type': 'URI',
                    'type': 'str',
                    'default': '\'FIXME: Provide default\'',
                    'default_arg': 'None',
                    'validation': 'is_valid_uri(%s)',
                    'doc': (
                        'Format of the data streaming through the link as an '
                        'URI'
                    )
                },
            ],
            'relations': [
                {
                    'name': 'hasLabel',
                    'with': ['Label'],
                    'cardinality': '1',
                    'doc': 'FIXME: hasLabel documentation'
                },
            ]
        },
        {
            'name': 'Service',
            'parent': 'Network Object',
            'brief': 'FIXME: Service brief documentation',
            'doc': 'FIXME: Service documentation',
            'abstract': True,
            'attributes': [
            ],
            'relations': [
            ]
        },
        {
            'name': 'Switching Service',
            'parent': 'Service',
            'brief': 'FIXME: Service brief documentation',
            'doc': 'FIXME: Service documentation',
            'abstract': False,
            'attributes': [
                {
                    'name': 'encoding',
                    'property': True,
                    'nml_attribute': 'encoding',
                    'semantic_type': 'URI',
                    'type': 'str',
                    'default': '\'FIXME: Provide default\'',
                    'default_arg': 'None',
                    'validation': 'is_valid_uri(%s)',
                    'doc': (
                        'Format of the data streaming through the service as '
                        'an URI'
                    )
                },
            ],
            'relations': [
                {
                    'name': 'hasInboundPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: hasInboundPort documentation'
                },
                {
                    'name': 'hasOutboundPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: hasOutboundPort documentation'
                },
                {
                    'name': 'providesLink',
                    'with': ['Link', 'Link Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: providesLink documentation'
                },
            ]
        },
        {
            'name': 'Adaptation Service',
            'parent': 'Service',
            'brief': 'FIXME: Service brief documentation',
            'doc': 'FIXME: Service documentation',
            'abstract': False,
            'attributes': [
                {
                    'name': 'adaptation_function',
                    'property': False,
                    'nml_attribute': 'adaptationFunction',
                    'semantic_type': None,
                    'type': None,
                    'default': None,
                    'default_arg': None,
                    'validation': None,
                    'doc': 'Function for multiplexing'
                }
            ],
            'relations': [
                {
                    'name': 'canProvidePort',
                    'with': ['Port', 'PortGroup'],
                    'cardinality': '+',
                    'doc': 'FIXME: canProvidePort documentation'
                },
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: existsDuring documentation'
                },
                {
                    'name': 'providesPort',
                    'with': ['Port', 'PortGroup'],
                    'cardinality': '+',
                    'doc': 'FIXME: providesPort documentation'
                }
            ]
        },
        {
            'name': 'De-adaptation Service',
            'parent': 'Service',
            'brief': 'FIXME: Service brief documentation',
            'doc': 'FIXME: Service documentation',
            'abstract': False,
            'attributes': [
                {
                    'name': 'adaptation_function',
                    'property': False,
                    'nml_attribute': 'adaptationFunction',
                    'semantic_type': None,
                    'type': None,
                    'default': None,
                    'default_arg': None,
                    'validation': None,
                    'doc': 'Function for multiplexing'
                }
            ],
            'relations': [
                {
                    'name': 'canProvidePort',
                    'with': ['Port', 'PortGroup'],
                    'cardinality': '+',
                    'doc': 'FIXME: canProvidePort documentation'
                },
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: existsDuring documentation'
                },
                {
                    'name': 'providesPort',
                    'with': ['Port', 'PortGroup'],
                    'cardinality': '+',
                    'doc': 'FIXME: providesPort documentation'
                }
            ]
        },
        {
            'name': 'Group',
            'parent': 'Network Object',
            'brief': 'FIXME: Group brief documentation',
            'doc': 'FIXME: Group documentation',
            'abstract': True,
            'attributes': [
            ],
            'relations': [
            ]
        },
        {
            'name': 'Topology',
            'parent': 'Group',
            'brief': 'FIXME: Topology brief documentation',
            'doc': 'FIXME: Topology documentation',
            'abstract': False,
            'attributes': [
            ],
            'relations': [
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: existsDuring documentation'
                },
                {
                    'name': 'hasNode',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: hasNode documentation'
                },
                {
                    'name': 'hasInboundPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: hasInboundPort documentation'
                },
                {
                    'name': 'hasOutboundPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: hasOutboundPort documentation'
                },
                {
                    'name': 'hasService',
                    'with': ['Switching Service'],
                    'cardinality': '+',
                    'doc': 'FIXME: hasService documentation'
                },
                {
                    'name': 'hasTopology',
                    'with': ['Topology'],
                    'cardinality': '+',
                    'doc': 'FIXME: hasTopology documentation'
                }
            ]
        },
        {
            'name': 'Port Group',
            'parent': 'Group',
            'brief': 'FIXME: Group brief documentation',
            'doc': 'FIXME: Group documentation',
            'abstract': False,
            'attributes': [
            ],
            'relations': [
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: existsDuring documentation'
                },
                {
                    'name': 'hasLabelGroup',
                    'with': ['Lifetime'],
                    'cardinality': '1',
                    'doc': 'FIXME: hasLabelGroup documentation'
                },
                {
                    'name': 'hasPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'fixme: hasPort documentation'
                },
                {
                    'name': 'isSink',
                    'with': ['LinkGroup'],
                    'cardinality': '+',
                    'doc': 'FIXME: isSink documentation'
                },
                {
                    'name': 'isSource',
                    'with': ['LinkGroup'],
                    'cardinality': '+',
                    'doc': 'FIXME: isSource documentation'
                },
            ]
        },
        {
            'name': 'Link Group',
            'parent': 'Group',
            'brief': 'FIXME: Group brief documentation',
            'doc': 'FIXME: Group documentation',
            'abstract': False,
            'attributes': [
            ],
            'relations': [
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: existsDuring documentation'
                },
                {
                    'name': 'hasLabelGroup',
                    'with': ['Lifetime'],
                    'cardinality': '1',
                    'doc': 'FIXME: hasLabelGroup documentation'
                },
                {
                    'name': 'hasLink',
                    'with': ['Port', 'PortGroup'],
                    'cardinality': '+',
                    'doc': 'fixme: hasport documentation'
                },
                {
                    'name': 'isSerialCompoundLink',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'fixme: hasport documentation'
                }
            ]
        },
        {
            'name': 'Bidirectional Port',
            'parent': 'Group',
            'brief': 'FIXME: Port brief documentation',
            'doc': 'FIXME: Port documentation',
            'abstract': False,
            'attributes': [
            ],
            'relations': [
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: existsDuring documentation'
                },
                {
                    'name': 'hasPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '2',
                    'doc': 'fixme: hasPort documentation'
                }
            ]
        },
        {
            'name': 'Bidirectional Link',
            'parent': 'Group',
            'brief': 'FIXME: Link brief documentation',
            'doc': 'FIXME: Link documentation',
            'abstract': False,
            'attributes': [
            ],
            'relations': [
            ]
        },
        {
            'name': 'Location',
            'parent': None,
            'brief': 'FIXME: Location brief documentation',
            'doc': 'FIXME: Location documentation',
            'abstract': False,
            'attributes': [
            ],
            'relations': [
            ]
        },
        {
            'name': 'Lifetime',
            'parent': None,
            'brief': 'FIXME: Lifetime brief documentation',
            'doc': 'FIXME: Lifetime documentation',
            'abstract': False,
            'attributes': [
            ],
            'relations': [
            ]
        },
        {
            'name': 'Label',
            'parent': None,
            'brief': 'FIXME: Label brief documentation',
            'doc': 'FIXME: Label documentation',
            'abstract': False,
            'attributes': [
            ],
            'relations': [
            ]
        },
        {
            'name': 'Label Group',
            'parent': None,
            'brief': 'FIXME: Group brief documentation',
            'doc': 'FIXME: Group documentation',
            'abstract': False,
            'attributes': [
            ],
            'relations': [
            ]
        },
        {
            'name': 'Ordered List',
            'parent': None,
            'brief': 'FIXME: List brief documentation',
            'doc': 'FIXME: List documentation',
            'abstract': False,
            'attributes': [
            ],
            'relations': [
            ]
        },
        {
            'name': 'List Item',
            'parent': None,
            'brief': 'FIXME: Item brief documentation',
            'doc': 'FIXME: Item documentation',
            'abstract': False,
            'attributes': [
            ],
            'relations': [
            ]
        },
    ]
}

NML_TEMPLATE = """\
{%- macro param_attrs(attrs) -%}
{% if attrs -%}
, {% for attr in attrs -%}
{{ attr.name|variablize }}={{ attr.default_arg }}
{%- if not loop.last %}, {% endif -%}
{%- endfor %}
{%- endif %}
{%- endmacro -%}
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

\"""
pynml main module.
\"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

from datetime import datetime
from collections import OrderedDict
from abc import ABCMeta, abstractmethod
from xml.etree import ElementTree as etree  # noqa

from rfc3986 import is_valid_uri

from .exceptions import (
    {%- for exc in exceptions %}
    {{ exc }}{% if not loop.last %},{% endif %}
    {%- endfor %}
)


NAMESPACES = {'nml': 'http://schemas.ogf.org/nml/2013/05/base'}


def tree_element(self, this, parent):
    \"""
    Helper function to identify an XML node to modify in a inheritance and
    multi-node tree.
    \"""
    if this is None:
        if parent is None:
            this = etree.Element(
                self.__class__.__name__, nsmap=NAMESPACES
            )
        else:
            this = etree.SubElement(
                parent, self.__class__.__name__, nsmap=NAMESPACES
            )
    return this


{% for cls in spec.classes -%}
class {{ cls.name|objectize }}({{ cls.parent|objectize|default('object', True) }}):
    \"""
    {{ cls.brief|wordwrap(75)|indent(4) }}.

    {{ cls.doc|wordwrap(75)|indent(4) }}.

    {% for attr in cls.attributes -%}
    {{ ':param %s %s: %s.'|format(attr.type, attr.name, attr.doc)|wordwrap(71)|indent(9) }}
    {% endfor -%}
    \"""
    {%- if cls.abstract %}
    __metaclass__ = ABCMeta
    {%- endif %}
{##}
    {%- if cls.abstract %}
    @abstractmethod
    {%- endif %}
    def __init__(self{{ param_attrs(cls.attributes) }}, **kwargs):
        {%- if cls.parent is not none %}
        super({{ cls.name|objectize }}, self).__init__(**kwargs)
{##}
        {%- endif %}
        # Attributes
        {%- for attr in cls.attributes %}
        {%- if attr.property %}
        if {{ attr.name }} is {{ attr.default_arg }}:
            {{ attr.name }} = {{ attr.default }}
        self.{{ attr.name }} = {{ attr.name }}
        {%- else %}
        self.{{ attr.name }} = {{ attr.name }}
        {%- endif %}
{##}
        {%- endfor %}
        # Relations
        {%- for rel in cls.relations %}
        {%- set relation_collection =  rel.name|variablize + '_' + rel.with.0|pluralize|variablize %}
        self._{{ relation_collection }} = {##}
        {%- if rel.cardinality == '+' -%}
        OrderedDict()
        {%- else -%}
        ({{ 'None, ' * rel.cardinality|int }})
        {%- endif %}
        {%- endfor %}

        {%- if cls.parent is none %}
{##}
        self.metadata = kwargs
        {%- endif %}
{##}
    {%- for attr in cls.attributes %}
    {%- if attr.property %}
    @property
    def {{ attr.name }}(self):
        \"""
        Get attribute {{ attr.name }}.

        {{ ':return: %s.'|format(attr.doc)|wordwrap(71)|indent(9) }}
        :rtype: {{ attr.type }}
        \"""
        return self._{{ attr.name }}

    @{{ attr.name }}.setter
    def {{ attr.name }}(self, {{ attr.name }}):
        \"""
        Set attribute {{ attr.name }}.

        {{ ':param %s %s: %s.'|format(attr.type, attr.name, attr.doc)|wordwrap(71)|indent(9) }}
        \"""
        {%- if attr.validation is not none %}
        if not {{ attr.validation|format(attr.name) }}:
            raise Attribute{{ attr.nml_attribute|objectize }}Error()
        self._{{ attr.name }} = {{ attr.name }}
        {%- else %}
        self._{{ attr.name }} = {{ attr.name }}
        {%- endif %}
{##}
    {%- endif %}
    {%- endfor %}

    {%- for rel in cls.relations %}
    {%- set argument = rel.with.0|variablize %}
    {%- set relation_collection =  rel.name|variablize + '_' + rel.with.0|pluralize|variablize %}
    def {{ rel.name|methodize }}(self, {{ argument }}):
        \"""
        {{ 'Check `%s` relation with given `%s` object.'|format(rel.name, argument)|wordwrap(71)|indent(8) }}

        {{ rel.doc|wordwrap(71)|indent(8) }}.

        {{ ':param %s: Object to validate relation `%s` with.'|format(argument, rel.name)|wordwrap(71)|indent(9) }}
        :type {{ argument }}: {{ rel.with|map('objectize')|join(' or ') }}
        {{ ':return: True if `%s` is related to `self` with `%s`.'|format(argument, rel.name)|wordwrap(71)|indent(9) }}
        :rtype: bool
        \"""
        if {{ argument }}.__class__ not in (
            {%- for with in rel.with %}
                {{ with|objectize }}{% if not loop.last %},{% endif %}
            {%- endfor %}, ):
            raise Relation{{ rel.name|objectize }}Error()

        return {{ argument }}
        {%- if rel.cardinality == '+' %}.identifier{% endif %} in \\
            self._{{ relation_collection }}
{##}
    {%- if rel.cardinality == '+' %}
    def add_{{ rel.name|variablize }}(self, {{ argument }}):
        \"""
        Add given `{{ argument }}` to this object `{{ rel.name }}` relations.

        {{ ':param %s: Object to add to the `%s` relation.'|format(argument, rel.name)|wordwrap(71)|indent(9) }}
        :type {{ argument }}: {{ rel.with|map('objectize')|join(' or ') }}
        \"""
        if {{ argument }}.__class__ not in (
            {%- for with in rel.with %}
                {{ with|objectize }}{% if not loop.last %},{% endif %}
            {%- endfor %}, ):
            raise Relation{{ rel.name|objectize }}Error()

        self._{{ relation_collection }}[{{ argument }}.identifier] = \\
            {{ argument }}
    {%- else %}
    {%- if rel.cardinality|int > 1 %}
    {%- set arguments = argument + range(1, rel.cardinality|int + 1)|join(', ' + argument) %}
    {%- else %}
    {%- set arguments = argument %}
    {%- endif %}
    def set_{{ rel.name|variablize }}(self, {{ arguments }}):
        \"""
        Set the `{{ rel.name }}` relation to given objects.
{##}
        {%- if rel.cardinality|int > 1 %}
        {%- for i in range(1, rel.cardinality|int + 1) %}
        :param {{ argument }}{{ i }}: One of the objects to set the `{{ rel.name }}` relation.
        :type {{ argument }}{{ i }}: {{ rel.with|map('objectize')|join(' or ') }}
        {%- endfor %}
        {%- else %}
        :param {{ argument }}: Object to set to the `{{ rel.name }}` relation.
        :type {{ argument }}: {{ rel.with|map('objectize')|join(' or ') }}
        {%- endif %}
        \"""
        if {{ argument }}.__class__ not in ({{ rel.with|map('objectize')|join(', ') }}, ):
            raise Relation{{ rel.name|objectize }}Error()

        arg_tuple = ({{ arguments }}, )
        {%- if rel.cardinality|int > 1 %}
        if len(set(arg_tuple)) != len(arg_tuple):
            raise Exception('Non unique objects')  # FIXME
        {%- endif %}

        self._{{ relation_collection }} = arg_tuple
    {%- endif %}
{##}
    {%- endfor %}

    {%- if cls.abstract %}
    @abstractmethod
    {%- endif %}
    def as_nml(self, this=None, parent=None):
        \"""
        {%- if cls.parent is none %}
        Build NML representation of this node.

        :param this: Node to modify. If `None`, a new node is created.
        :type this: :py:class:`xml.etree.ElementTree`
        :param parent: Parent node to hook to. If `None`, a root node is
         created.
        :type parent: :py:class:`xml.etree.ElementTree`
        :rtype: :py:class:`xml.etree.ElementTree`
        :return: The NML representation of this node.
        {%- else %}
        See :meth:`{{ cls.parent|objectize }}.as_nml`.
        {%- endif %}
        \"""
        this = tree_element(self, this, parent)

        # Attributes
        {%- for attr in cls.attributes %}
        this.attrib['{{ attr.nml_attribute}}'] = self._{{ attr.name }}
        {%- endfor %}

        # Relations
        {%- for rel in cls.relations %}
        {%- set iterator = rel.with.0|variablize %}
        {%- set collection = rel.with.0|pluralize|variablize %}
        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = '{{ rel.name }}'
        for {{ iterator }} in self._{{ collection }}:
            reference = etree.SubElement(
                relation, {{ iterator }}.__class__.__name__
            )
            reference.attrib['id'] = {{ iterator }}.identifier
{##}
        {%- endfor %}
        {%- if cls.parent is not none %}
        # Parent attributes and relations
        super({{ cls.name|objectize }}, self).as_nml(this, parent)
{##}
        {%- endif %}
        return this


{% endfor -%}
__all__ = [
{%- for cls in spec.classes %}
    '{{ cls.name|objectize }}'{% if not loop.last %},{% endif %}
{%- endfor %}
]

"""  # noqa


EXCEPTIONS_TEMPLATE = """\
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

\"""
pynml exceptions module.
\"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division


class NMLException(Exception):
    \"""
    Base NML Exception class.
    \"""
    def __str__(self):
        return ' '.join(self.__class__.__doc__.split())

    def __repr__(self):
        return repr(str(self))


{% for exc, doc in exceptions.items() -%}
class {{ exc }}(NMLException):
    \"""
    {{ doc|wordwrap(75)|indent(4) }}.
    \"""


{% endfor -%}
__all__ = [
{%- for exc in exceptions %}
    '{{ exc }}'{% if not loop.last %},{% endif %}
{%- endfor %}
]

"""  # noqa


def filter_objectize(token):
    if token is None:
        return None
    return camelize(underscore(parameterize(underscore(token))))


def filter_methodize(token):
    if token is None:
        return None
    return underscore(parameterize(underscore(token)))


def filter_variablize(token):
    if token is None:
        return None
    return underscore(parameterize(underscore(token)))


def filter_pluralize(token):
    if token is None:
        return None
    return pluralize(token)


def build():
    """
    Build NML Python module from specification.
    """
    # Gather data
    exceptions = OrderedDict()
    for cls in NML_SPEC['classes']:
        for rel in cls['relations']:
            exc_name = 'Relation{}Error'.format(
                filter_objectize(rel['name'])
            )
            exceptions[exc_name] = rel['doc']
    for cls in NML_SPEC['classes']:
        for attr in cls['attributes']:
            if attr['validation'] is not None:
                exc_name = 'Attribute{}Error'.format(
                    filter_objectize(attr['nml_attribute'])
                )
                exceptions[exc_name] = attr['doc']

    # Build template environment
    def load_template(name):
        templates = {
            'nml': NML_TEMPLATE,
            'exceptions': EXCEPTIONS_TEMPLATE
        }
        return templates[name]

    env = Environment(
        loader=FunctionLoader(load_template),
        undefined=StrictUndefined
    )
    for ftr in ['objectize', 'methodize', 'variablize', 'pluralize']:
        env.filters[ftr] = globals()['filter_' + ftr]

    for tpl in ['nml', 'exceptions']:

        # Render template
        template = env.get_template(tpl)
        rendered = template.render(
            spec=NML_SPEC,
            exceptions=exceptions
        )

        # Write output
        root = dirname(normpath(abspath(__file__)))

        with open(join(root, 'n{}.py'.format(tpl)), 'w') as module:
            module.write(rendered)


__all__ = ['NML_SPEC']


if __name__ == '__main__':
    build()
