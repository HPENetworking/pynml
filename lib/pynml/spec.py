# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Hewlett Packard Enterprise Development LP
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
            'brief': 'The basic class from other instances inherit from',
            'doc': (
                'No NetworkObject instances can be created because '
                'this class is abstract'
            ),
            'abstract': True,
            'attributes': [
                {
                    'name': 'name',
                    'property': True,
                    'nml_attribute': 'name',
                    'semantic_type': 'string',
                    'type': 'str',
                    'default': (
                        '\'{}({})\'.format(\n'
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
                    'doc': 'FIXME: Document existsDuring relation'
                },
                {
                    'name': 'isAlias',
                    'with': ['Network Object'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document isAlias relation'
                },
                {
                    'name': 'locatedAt',
                    'with': ['Location'],
                    'cardinality': '1',
                    'doc': 'FIXME: Document locatedAt relation'
                },
            ]
        },
        {
            'name': 'Node',
            'parent': 'Network Object',
            'brief': 'A Node object represents a device in a network',
            'doc': (
                'Physical or virtual devices can be represented '
                'by instances of this class'
            ),
            'abstract': False,
            'attributes': [
            ],
            'relations': [
                {
                    'name': 'hasInboundPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasInboundPort relation'
                },
                {
                    'name': 'hasOutboundPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasOutboundPort relation'
                },
                {
                    'name': 'hasService',
                    'with': ['Switching Service'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasService relation'
                },
                {
                    'name': 'implementedBy',
                    'with': ['Node'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document implementedBy relation'
                },
            ]
        },
        {
            'name': 'Port',
            'parent': 'Network Object',
            'brief': 'Endpoint of an unidirectional connection',
            'doc': (
                'Can represent physical or virtual ports. Needs a proper '
                'linking instance to connect to other ports'
            ),
            'abstract': False,
            'attributes': [
                {
                    'name': 'encoding',
                    'property': True,
                    'nml_attribute': 'encoding',
                    'semantic_type': 'URI',
                    'type': 'str',
                    'default': 'unset',
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
                    'doc': 'FIXME: Document hasLabel relation'
                },
                {
                    'name': 'hasService',
                    'with': ['Adaptation Service', 'De-adaptation Service'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasService relation'
                },
                {
                    'name': 'isSink',
                    'with': ['Link'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document isSink relation'
                },
                {
                    'name': 'isSource',
                    'with': ['Link'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document isSource relation'
                },
            ]
        },
        {
            'name': 'Link',
            'parent': 'Network Object',
            'brief': 'Connects a source object with a sink one',
            'doc': (
                'Sources and sinks have specified isSource or isSink '
                'relations with the Link instance but not vice versa'
            ),
            'abstract': False,
            'attributes': [
                {
                    'name': 'encoding',
                    'property': True,
                    'nml_attribute': 'encoding',
                    'semantic_type': 'URI',
                    'type': 'str',
                    'default': 'unset',
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
                    'doc': 'FIXME: Document hasLabel relation'
                },
            ]
        },
        {
            'name': 'Service',
            'parent': 'Network Object',
            'brief': 'Base class for services that a network may provide',
            'doc': (
                'No Service instances can be created because '
                'this class is abstract'
            ),
            'abstract': True,
            'attributes': [
            ],
            'relations': [
            ]
        },
        {
            'name': 'Switching Service',
            'parent': 'Service',
            'brief': (
                'Shows that the network can create new links between '
                'certain ports'
            ),
            'doc': (
                'An instance of this class shows that the network is capable '
                'of creating new Links or LinkGroups between its inbound and '
                'outbound ports. These Links or LinkGroups are identified by '
                'being related to the SwitchingService instance with a '
                'providesLink relation'
            ),
            'abstract': False,
            'attributes': [
                {
                    'name': 'encoding',
                    'property': True,
                    'nml_attribute': 'encoding',
                    'semantic_type': 'URI',
                    'type': 'str',
                    'default': 'unset',
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
                    'doc': 'FIXME: Document hasInboundPort relation'
                },
                {
                    'name': 'hasOutboundPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasOutboundPort relation'
                },
                {
                    'name': 'providesLink',
                    'with': ['Link', 'Link Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document providesLink relation'
                },
            ]
        },
        {
            'name': 'Adaptation Service',
            'parent': 'Service',
            'brief': (
                'Shows that the network can embed data from one or more '
                'Ports or PortGroups into other Ports or PortGroups'
            ),
            'doc': (
                'An instance of this class shows that data from one or more '
                'Ports can be embedded in the data encoding of other Port or '
                'Ports. This class has an adaptationFunction attribute that '
                'should describe the kind of embedding that is used by the '
                'AdaptationService instance'
            ),
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
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document canProvidePort relation'
                },
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document existsDuring relation'
                },
                {
                    'name': 'providesPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document providesPort relation'
                }
            ]
        },
        {
            'name': 'De-adaptation Service',
            'parent': 'Service',
            'brief': (
                'Shows that the network can extract data from one or more '
                'Ports or PortGroups encoding'
            ),
            'doc': (
                'An instance of this class shows that data from one or more '
                'Ports can be extracted from the data encoding of other Port '
                'or Ports. This class has an adaptationFunction attribute '
                'that should describe the kind of extraction that is used by '
                'the DeadaptationService instance'
            ),
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
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document canProvidePort relation'
                },
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document existsDuring relation'
                },
                {
                    'name': 'providesPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document providesPort relation'
                }
            ]
        },
        {
            'name': 'Group',
            'parent': 'Network Object',
            'brief': 'A collection of objects',
            'doc': (
                'Any object can be part of a Group, even another Group. '
                'An object can be part of multiple Groups'
            ),
            'abstract': True,
            'attributes': [
            ],
            'relations': [
            ]
        },
        {
            'name': 'Topology',
            'parent': 'Group',
            'brief': 'A set of connected or connectable Network objects',
            'doc': (
                'One or more Link or LinkGroup objects can provide the '
                'connection between the Topology Network Objects'
            ),
            'abstract': False,
            'attributes': [
            ],
            'relations': [
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document existsDuring relation'
                },
                {
                    'name': 'hasNode',
                    'with': ['Node'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasNode relation'
                },
                {
                    'name': 'hasInboundPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasInboundPort relation'
                },
                {
                    'name': 'hasOutboundPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasOutboundPort relation'
                },
                {
                    'name': 'hasService',
                    'with': ['Switching Service'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasService relation'
                },
                {
                    'name': 'hasEnvironment',
                    'with': ['Environment'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasEnvironment relation'
                },
                {
                    'name': 'hasTopology',
                    'with': ['Topology'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasTopology relation'
                }
            ]
        },
        {
            'name': 'Port Group',
            'parent': 'Group',
            'brief': 'A unordered set of Ports',
            'doc': 'FIXME: Document PortGroup',
            'abstract': False,
            'attributes': [
            ],
            'relations': [
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document existsDuring relation'
                },
                {
                    'name': 'hasLabelGroup',
                    'with': ['Lifetime'],
                    'cardinality': '1',
                    'doc': 'FIXME: Document hasLabelGroup relation'
                },
                {
                    'name': 'hasPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasPort relation'
                },
                {
                    'name': 'isSink',
                    'with': ['Link Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document isSink relation'
                },
                {
                    'name': 'isSource',
                    'with': ['Link Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document isSource relation'
                },
            ]
        },
        {
            'name': 'Link Group',
            'parent': 'Group',
            'brief': 'A unordered set of Links',
            'doc': 'FIXME: Document LinkGroup',
            'abstract': False,
            'attributes': [
            ],
            'relations': [
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document existsDuring relation'
                },
                {
                    'name': 'hasLabelGroup',
                    'with': ['Lifetime'],
                    'cardinality': '1',
                    'doc': 'FIXME: Document hasLabelGroup relation'
                },
                {
                    'name': 'hasLink',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasLink relation'
                },
                {
                    'name': 'isSerialCompoundLink',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document isSerialCompoundLink relation'
                }
            ]
        },
        {
            'name': 'Bidirectional Port',
            'parent': 'Group',
            'brief': 'A group of two unidirectional Ports or PortGroups',
            'doc': (
                'The purpose of this class is to provide a convenient '
                'representation of a bidirectional Port. This is needed '
                'because NML is a unidirectional specification'
            ),
            'abstract': False,
            'attributes': [
            ],
            'relations': [
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document existsDuring relation'
                },
                {
                    'name': 'hasPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '2',
                    'doc': 'FIXME: Document hasPort relation'
                }
            ]
        },
        {
            'name': 'Bidirectional Link',
            'parent': 'Group',
            'brief': 'A group of two unidirectional Links or LinkGroups',
            'doc': (
                'The purpose of this class is to provide a convenient '
                'representation of a bidirectional Link. This is needed '
                'because NML is a unidirectional specification'
            ),
            'abstract': False,
            'attributes': [
            ],
            'relations': [
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document existsDuring relation'
                },
                {
                    'name': 'hasLink',
                    'with': ['Link', 'Link Group'],
                    'cardinality': '2',
                    'doc': 'FIXME: Document hasLink relation'
                }
            ]
        },
        {
            'name': 'Environment',
            'parent': None,
            'brief': 'Describes attributes inherent to the environment',
            'doc': (
                'Attributes to be attached to the environment the topology is '
                'in.'
            ),
            'abstract': False,
            'attributes': [
            ],
            'relations': [
            ]
        },
        {
            'name': 'Location',
            'parent': None,
            'brief': 'Describes where the object is physically located',
            'doc': (
                'An instance of this class can be related to other objects '
                'that are to be represented as being present in the same '
                'place'
            ),
            'abstract': False,
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
                    'name': 'longitude',
                    'property': True,
                    'nml_attribute': 'long',
                    'semantic_type': 'WGS84',
                    'type': 'str',
                    'default': 'unset',
                    'default_arg': 'None',
                    'validation': None,  # FIXME Add WGS84 validation
                    'doc': 'Longitude in WGS84 and in decimal degrees'
                },
                {
                    'name': 'latitude',
                    'property': True,
                    'nml_attribute': 'lat',
                    'semantic_type': 'WGS84',
                    'type': 'str',
                    'default': 'unset',
                    'default_arg': 'None',
                    'validation': None,  # FIXME Add WGS84 validation
                    'doc': 'Latitude in WGS84 and in decimal degrees'
                },
                {
                    'name': 'altitude',
                    'property': True,
                    'nml_attribute': 'alt',
                    'semantic_type': 'WGS84',
                    'type': 'str',
                    'default': 'unset',
                    'default_arg': 'None',
                    'validation': None,  # FIXME Add WGS84 validation
                    'doc': 'Altitude in WGS84 and in decimal meters'
                },
                {
                    'name': 'unlocode',
                    'property': True,
                    'nml_attribute': 'unlocode',
                    'semantic_type': 'UN/LOCODE',
                    'type': 'str',
                    'default': 'unset',
                    'default_arg': 'None',
                    'validation': None,  # FIXME Add UN/LOCODE validation
                    'doc': 'UN/LOCODE location identifier'
                },
                {
                    'name': 'address',
                    'property': True,
                    'nml_attribute': 'address',
                    'semantic_type': 'vCard ADR',
                    'type': 'str',
                    'default': 'unset',
                    'default_arg': 'None',
                    'validation': None,  # FIXME Add vCard ADR validation
                    'doc': 'A vCard ADR property'
                }
            ],
            'relations': [
            ]
        },
        {
            'name': 'Lifetime',
            'parent': None,
            'brief': 'A time interval where the object is active',
            'doc': (
                'An object can have multiple Lifetimes, if so, it will be '
                'active in a time interval equivalent to the union of all '
                'its Lifetimes time intervals'
            ),
            'abstract': False,
            'attributes': [
                {
                    'name': 'start',
                    'property': True,
                    'nml_attribute': 'start',
                    'semantic_type': 'timestamp',
                    'type': 'str',
                    'default': (
                        'datetime.now().replace(microsecond=0).isoformat()'
                    ),
                    'default_arg': 'None',
                    'validation': None,  # FIXME Add ISO 8601 validation
                    'doc': (
                        'Date and time formatted as ISO 8601 calendar date '
                        'compact representation with UTC timezone '
                        '(YYYYMMDDThhmmssZ)'
                    )
                },
                {
                    'name': 'end',
                    'property': True,
                    'nml_attribute': 'end',
                    'semantic_type': 'timestamp',
                    'type': 'str',
                    'default': (
                        'datetime.now().replace(microsecond=0).isoformat()'
                    ),
                    'default_arg': 'None',
                    'validation': None,  # FIXME Add ISO 8601 validation
                    'doc': (
                        'Date and time formatted as ISO 8601 calendar date '
                        'compact representation with UTC timezone '
                        '(YYYYMMDDThhmmssZ)'
                    )
                }
            ],
            'relations': [
            ]
        },
        {
            'name': 'Label',
            'parent': None,
            'brief': 'A value that specifies a single data stream among many',
            'doc': (
                'A Label is technology-specific, so a Label used to identify '
                'a VLAN would be different from a Label used to identify a '
                'wavelength'
            ),
            'abstract': False,
            'attributes': [
                {
                    'name': 'labeltype',
                    'property': False,
                    'nml_attribute': 'labeltype',
                    'semantic_type': None,
                    'type': None,
                    'default': None,
                    'default_arg': None,
                    'validation': None,
                    'doc': 'A technology-specific labelset'
                },
                {
                    'name': 'value',
                    'property': False,
                    'nml_attribute': 'value',
                    'semantic_type': None,
                    'type': None,
                    'default': None,
                    'default_arg': None,
                    'validation': None,
                    'doc': 'A specific value taken from a labelset'
                }
            ],
            'relations': [
            ]
        },
        {
            'name': 'Label Group',
            'parent': None,
            'brief': 'A unordered set of Labels',
            'doc': 'FIXME: Document LabelGroup',
            'abstract': False,
            'attributes': [
                {
                    'name': 'labeltype',
                    'property': False,
                    'nml_attribute': 'labeltype',
                    'semantic_type': None,
                    'type': None,
                    'default': None,
                    'default_arg': None,
                    'validation': None,
                    'doc': 'A technology-specific labelset'
                },
                {
                    'name': 'value',
                    'property': False,
                    'nml_attribute': 'value',
                    'semantic_type': None,
                    'type': None,
                    'default': None,
                    'default_arg': None,
                    'validation': None,
                    'doc': 'A specific value taken from a labelset'
                }
            ],
            'relations': [
            ]
        },
        {
            'name': 'Ordered List',
            'parent': None,
            'brief': 'An ordered list of Network Objects',
            'doc': (
                'Instances of this class are used to describe a path in the '
                'network along with the isSerialCompoundLink relation'
            ),
            'abstract': False,
            'attributes': [
            ],
            'relations': [
            ]
        },
        {
            'name': 'List Item',
            'parent': None,
            'brief': 'An element of an OrderedList',
            'doc': (
                'Is a syntax-dependent object used to represent elements in '
                'an OrderedList'
            ),
            'abstract': False,
            'attributes': [
            ],
            'relations': [
            ]
        },
    ]
}
"""NML Specification as a Python dictionary"""


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
# Copyright (C) 2015-2016 Hewlett Packard Enterprise Development LP
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

from copy import copy
from datetime import datetime
from collections import OrderedDict
from abc import ABCMeta, abstractmethod
from xml.etree import ElementTree as etree  # noqa

from six import add_metaclass
from rfc3986 import is_valid_uri

from .exceptions import (
    {%- for exc in exceptions %}
    {{ exc }}{% if not loop.last %},{% endif %}
    {%- endfor %}
)


# Register XML namespaces
NAMESPACES = {'nml': 'http://schemas.ogf.org/nml/2013/05/base'}
for xmlns, uri in NAMESPACES.items():
    etree.register_namespace(xmlns, uri)

# Special unique variable for unset values
unset = type(str('Unset'), (object,), {})()


@add_metaclass(ABCMeta)
class NMLObject(object):
    \"""
    Base object for every NML object.

    This object is not part of the specification, it is just 'Pure Fabrication'
    (see GRASP) of refactored functionality of all objects.
    \"""

    @abstractmethod
    def __init__(self, **kwargs):
        self.attributes = []
        self.relations = OrderedDict()
        self.metadata = kwargs

    def _describe_object(self):
        \"""
        Describe and pretty-print the NML object.

        :rtype: str
        :return: A pretty-printed string with attributes and metadata.
        \"""
        name = self.__class__.__name__
        attributes = [
            (attr, getattr(self, attr))
            for attr in self.attributes + ['metadata']
            if hasattr(self, attr)
        ]
        formatted_attributes = ', '.join([
            '{}={}'.format(attr, repr(value)) for attr, value in attributes
        ])
        return '{}({})'.format(name, formatted_attributes)

    def __repr__(self):
        return self._describe_object()

    def __str__(self):
        return self._describe_object()

    def _tree_element(self, this, parent):
        \"""
        Helper function to identify an XML node to modify in a inheritance and
        multi-node tree.
        \"""
        if this is None:
            name = 'nml:' + self.__class__.__name__
            if parent is None:
                this = etree.Element(name)
            else:
                this = etree.SubElement(parent, name)
        return this

    def as_nml(self, this=None, parent=None):
        \"""
        Build NML representation of this node.

        :param this: Node to modify. If `None`, a new node is created.
        :type this: :py:class:`xml.etree.ElementTree`
        :param parent: Parent node to hook to. If `None`, a root node is
         created.
        :type parent: :py:class:`xml.etree.ElementTree`
        :rtype: :py:class:`xml.etree.ElementTree`
        :return: The NML representation of this node.
        \"""
        this = self._tree_element(this, parent)

        # Attributes
        for attr_name in self.attributes:
            attr = getattr(self, attr_name)
            if attr is not unset:
                this.attrib[attr_name] = attr

        # Relations
        for relname, relgetter in self.relations.items():

            # Composition elements are tuples
            # Aggregation elements are OrderedDict
            associated = relgetter()
            if isinstance(associated, OrderedDict):
                associated = associated.values()

            # Ignore empty relations
            if not associated or not all(associated):
                continue

            # Create subelement
            relation = etree.SubElement(
                this, 'Relation',
                type='{}#{}'.format(NAMESPACES['nml'], relname)
            )

            for associated in associated:
                etree.SubElement(
                    relation, associated.__class__.__name__,
                    id=associated.identifier
                )

        return this


{% for cls in spec.classes -%}
{%- if cls.abstract -%}
@add_metaclass(ABCMeta)
{% endif -%}
class {{ cls.name|objectize }}({{ cls.parent|objectize|default('NMLObject', True) }}):
    \"""
    {{ cls.brief|wordwrap(75)|indent(4) }}.

    {{ cls.doc|wordwrap(75)|indent(4) }}.
    {%- if cls.attributes %}
{##}
    {%- endif %}
    {% for attr in cls.attributes -%}
    {{ ':param %s %s: %s.'|format(attr.type, attr.name, attr.doc)|wordwrap(75)|indent(5) }}
    {% endfor -%}
    \"""
{##}
    {%- if cls.abstract %}
    @abstractmethod
    {%- endif %}
    def __init__(
            {{ 'self%s, **kwargs):'|format(param_attrs(cls.attributes))|wordwrap(67)|indent(12) }}
        super({{ cls.name|objectize }}, self).__init__(**kwargs)
        {%- if cls.attributes %}

        # Attributes
        {%- endif -%}
        {%- for attr in cls.attributes %}

        self.attributes.append('{{ attr.name }}')
        {%- if attr.property %}
        if {{ attr.name }} is {{ attr.default_arg }}:
            {{ attr.name }} = {{ attr.default }}
        self.{{ attr.name }} = {{ attr.name }}
        {%- else %}
        self.{{ attr.name }} = {{ attr.name }}
        {%- endif %}
        {%- endfor %}
        {%- if cls.relations %}
{##}
        # Relations
        {%- endif -%}
        {%- for rel in cls.relations %}
        self.relations['{{ rel.name }}'] = \\
            self.get_{{ rel.name|methodize }}
        {%- set relation_collection =  rel.name|variablize + '_' + rel.with.0|pluralize|variablize %}
        self._{{ relation_collection }} = {##}
        {%- if rel.cardinality == '+' -%}
        OrderedDict()
        {%- else -%}
        ({{ 'None, ' * rel.cardinality|int }})
        {%- endif %}
        {%- endfor %}
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
        if {{ attr.name }} is not unset and not {{ attr.validation|format(attr.name) }}:
            raise Attribute{{ attr.nml_attribute|objectize }}Error()
        self._{{ attr.name }} = {{ attr.name }}
        {%- else %}
        self._{{ attr.name }} = {{ attr.name }}
        {%- endif %}
    {%- endif -%}
    {%- endfor -%}
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
        arg_tuple = ({{ arguments }}, )

        for arg in arg_tuple:
            if arg.__class__ not in ({{ rel.with|map('objectize')|join(', ') }}, ):
                raise Relation{{ rel.name|objectize }}Error()

        {%- if rel.cardinality|int > 1 %}
        if len(set(arg_tuple)) != len(arg_tuple):
            raise Exception('Non unique objects')  # FIXME
        {%- endif %}

        self._{{ relation_collection }} = arg_tuple
    {%- endif %}
{##}
    def get_{{ rel.name|methodize }}(self):
        \"""
        {{ 'Get all objects related with this object with relation `%s`.'|format(rel.name)|wordwrap(71)|indent(8) }}

        :rtype: {% if rel.cardinality == '+' %}:py:class:`OrderedDict`{% else %}set{% endif %}
        :return: A copy of the collection of objects related with this object.
        \"""
        return copy(self._{{ relation_collection }})
    {%- endfor %}


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
# Copyright (C) 2015-2016 Hewlett Packard Enterprise Development LP
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
            exc_doc = (
                'A {} relation must relate with objects of type {}'.format(
                    rel['name'],
                    ' or '.join(
                        filter_objectize(w) for w in rel['with']
                    )
                )
            )
            exceptions[exc_name] = exc_doc

    def lower_first(string):
        return string[:1].lower() + string[1:] if string else ''

    for cls in NML_SPEC['classes']:
        for attr in cls['attributes']:
            if attr['validation'] is not None:
                exc_name = 'Attribute{}Error'.format(
                    filter_objectize(attr['nml_attribute'])
                )
                exceptions[exc_name] = 'Attribute `{}` must be a {}'.format(
                    attr['name'],
                    lower_first(attr['doc'])
                )

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

        with open(join(root, '{}.py'.format(tpl)), 'w') as module:
            module.write(rendered)


__all__ = ['NML_SPEC']


if __name__ == '__main__':
    build()
